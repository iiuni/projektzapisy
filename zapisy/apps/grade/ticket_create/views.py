import json

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll
from apps.grade.poll.utils import get_grouped_polls
from apps.grade.ticket_create.models import RSAKeys, StudentGraded
from apps.users.decorators import student_required


@student_required
def get_poll_data(request):
    """Lists Polls available to the student.

    The response follows the format:
    [
        # Every poll comes in a record.
        {
            "key": {
                "n": 12345...,
                "e": 12345...,
            },
            "poll_info": {
                "id": 123,
                # Name and Type only serve as a description. Name specifies the
                # exact poll (exam, group), Type says which course it concerns.
                "name": "Egzamin: Zbigniew Religa",
                "type": "Przeszczep serca dla zuchwałych",
            }
        },
    ]
    """
    students_polls = Poll.get_all_polls_for_student(request.user.student)
    keys = RSAKeys.objects.filter(poll__in=students_polls).select_related(
        'poll', 'poll__group', 'poll__course', 'poll__semester')
    response_data = []
    for key in keys:
        poll = key.poll
        poll_data = {
            'key': key.serialize_for_signing_protocol(),
            'poll_info': poll.serialize_for_signing_protocol(),
        }
        response_data.append(poll_data)
    return JsonResponse(response_data, safe=False)


@student_required
def tickets_generate(request):
    """Renders tickets_generate page and lists Polls student is entitled to."""
    semester = Semester.get_current_semester()
    is_grade_active = semester.is_grade_active
    if not is_grade_active:
        messages.error(
            request,
            "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów"
        )
        return redirect('grade-main')
    polls = get_grouped_polls(request.user.student)
    data = {
        'polls': polls,
        'is_grade_active': is_grade_active,
    }
    return render(request, 'ticket_create/tickets_generate.html', data)


@student_required
@transaction.atomic
def sign_tickets(request):
    """Signs the tickets sent by a student and returns list of signatures.

    The student must request to sign all the tickets he is entitled to. The
    signing may only be performed once in a semester.

    Request must be a dict of objects:
    {
        "signing_requests": [
            # An object for every poll.
            {
                # Id of the poll.
                "id": 123,
                # A blinded ticket.
                "ticket": 12345...,
            },
        ]
    }

    Returns:
        A list of signed tickets, each being a dict like below.
        {
            # Id of the poll.
            'id': 123,
            # The ticket from the request signed using a private key
            # corresponding to the poll.
            'signature': 1234...
        }

    Errors:
        400 BadRequest: When JSON request could not be parsed.
        403 Forbidden: When the student tries to sign a ticket for a poll he is
        not entitled to, fails to request a ticket he is entitled to, or has
        already been signing this semester.
    """
    try:
        signing_requests_dict = json.loads(request.body.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        return HttpResponseBadRequest("Couldn't parse JSON")

    signing_requests = signing_requests_dict['signing_requests']
    semester = Semester.get_current_semester()
    student_polls = {
        poll.pk for poll in Poll.get_all_polls_for_student(request.user.student, semester)
    }
    request_polls = {int(req['id']) for req in signing_requests}

    if request_polls - student_polls:
        return HttpResponseForbidden(
            f"Student nie jest upoważniony do tych ankiet: {request_polls - student_polls}.")
    if student_polls - request_polls:
        return HttpResponseForbidden("Student powinien również wygenerować bilety dla tych "
                                     "ankiet: {student_polls - request_polls}.")
    if len(request_polls) != len(signing_requests):
        return HttpResponseForbidden("Próbowano podpisać wiele biletów do jednej ankiety.")
    # Now we made sure that student_polls == request_polls

    # We obtain a lock on RSA keys.
    keys = RSAKeys.objects.filter(poll__in=request_polls).select_for_update()
    keys_by_poll = {key.poll_id: key for key in keys}

    _, created = StudentGraded.objects.get_or_create(student=request.user.student,
                                                     semester=semester)
    if not created:
        return HttpResponseForbidden("Student już podpisywał bilety w tym semestrze.")

    response = []
    for signing_request in signing_requests:
        key = keys_by_poll[int(signing_request['id'])]
        signed_ticket = key.sign_ticket(signing_request['ticket'])
        signing_response = {
            'id': signing_request['id'],
            'signature': str(signed_ticket),
        }
        response.append(signing_response)
    return JsonResponse(response, safe=False)
