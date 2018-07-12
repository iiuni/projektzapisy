from functools import reduce
from apps.grade.poll.models import Poll
from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.models import PublicKey, PrivateKey
from apps.grade.ticket_create.utils import group_polls_by_course, \
    generate_keys_for_polls, sign_ticket, \
    convert_ticket_record, connect_groups, get_valid_tickets, to_plaintext, \
    generate_ticket, secure_signer_without_save, mark_poll_used, Signature
from apps.users.decorators import student_required, employee_required
from apps.grade.ticket_create.models.student_graded import StudentGraded
from django.shortcuts import render
from django.contrib import messages
from django.core.cache import cache
from django.utils.safestring import SafeText
from apps.grade.ticket_create.forms import PollCombineForm


@student_required
def get_tickets(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        student_polls = Poll.get_all_polls_for_student(request.user.student)
        if student_polls:
            semester = student_polls[0].semester
        else:
            semester = None
        if request.method == "POST":
            grouped_polls = group_polls_by_course(student_polls)
            form = PollCombineForm(request.POST, polls=grouped_polls)

            if form.is_valid():
                connected_groups = connect_groups(grouped_polls, form)
                tickets = [generate_ticket(gs) for gs in
                           connected_groups]
                reduced_tickets = reduce(list.__add__, tickets)
                prepared_tickets = [(poll, int(ticket),
                                     secure_signer_without_save(request.user,
                                                                poll,
                                                                str(ticket)))
                                    for poll, ticket in reduced_tickets]

                for poll, _, _ in prepared_tickets:
                    mark_poll_used(request.user, poll)

                errors, tickets_to_serve = get_valid_tickets(prepared_tickets)
                if errors:
                    message = 'Nie udało się pobrać następujących biletów:\n<ul>'
                    for poll, reason in errors:
                        message += "<li>Ankieta: " + str(poll)
                        message += "<br>Powód: "
                        message += str(reason)
                        message += "</li>"
                    message += "</ul>"
                    messages.error(request, SafeText(message))

                if tickets_to_serve:
                    StudentGraded.objects.get_or_create(
                        student=request.user.student, semester=semester)

            return render(request, 'grade/ticket_create/tickets_save.html',
                          {'tickets': to_plaintext(tickets_to_serve),
                           'grade': grade})
        else:
            polls_list, general_polls = Poll.get_polls_list(
                request.user.student)
            return render(request, 'grade/ticket_create/get_tickets.html',
                          {'polls': polls_list, 'grade': grade,
                           'general_polls': general_polls})
    else:
        messages.error(request,
                       "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'grade/ticket_create/get_tickets.html',
                      {'grade': grade})


@student_required
def keys_list(request):
    """
        Strona, z ktorej student moze pobrac klucze publiczne ankiet, ktore ma prawo wypelnic
    """
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    polls = [x.pk for x in
             Poll.get_all_polls_for_student(request.user.student)]
    keys = PublicKey.objects.filter(poll_id__in=polls)
    return render(request, 'grade/ticket_create/keys_list.html',
                  {'public_keys': keys, 'grade': grade})


def sign_tickets(request):
    """
        Student przekazuje swoje kupony do podpisu kluczami prywatnymi przedmiotow
    """
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if request.method == 'POST':
        ticket_str = request.POST['tickets']
        if ticket_str:
            tmp = ticket_str.split('**********************************')
            signatures = []
            try:
                tickets = map(convert_ticket_record, tmp)
                for ticket in tickets:
                    if ticket:
                        poll_id = ticket[0]
                        key = PrivateKey.objects.get(poll_id=poll_id)
                        result = sign_ticket(ticket[1], key)
                        signatures.append(Signature(poll_id, result))
                return render(request,
                              'grade/ticket_create/signed_tickets.html',
                              {'signatures': signatures, 'grade': grade})
            except Exception as e:
                print('exception:' + str(e))
                messages.error(request, "Nie udało się podpisać kluczy")
        else:
            messages.info(request, "Nie podano kuponów do podpisu")
    return render(request, 'grade/ticket_create/sign_tickets.html',
                  {'grade': grade})


@employee_required
def keys_generate(request):
    """
        Widok odpowiadajacy za generowanie kluczy RSA dla ankiet
    """
    if request.method == 'POST':
        generate_keys_for_polls()
    count = cache.get('generated-keys', 0)
    without_keys = Poll.count_polls_without_keys()
    return render(request, 'grade/ticket_create/keys_generate.html',
                  {'progress_val': (count / without_keys) * 100})
