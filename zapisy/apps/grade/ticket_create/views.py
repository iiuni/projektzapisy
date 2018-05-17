# -*- coding: utf-8 -*-
import json

from apps.enrollment.courses.models import Semester
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.forms import PollCombineForm
from apps.grade.ticket_create.models import PublicKey, PrivateKey
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.grade.ticket_create.utils import generate_keys_for_polls, group_polls_by_course, \
    get_valid_tickets, to_plaintext, connect_groups, secure_mark, \
    sign_ticket, convert_ticket_record, Signature
from apps.users.decorators import student_required
from django.contrib import messages
from django.shortcuts import render
from django.utils.safestring import SafeUnicode


@student_required
def connections_choice(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    students_polls = Poll.get_all_polls_for_student(request.user.student)
    if students_polls:
        semester = students_polls[0].semester
    else:
        semester = None
    grouped_polls = group_polls_by_course(students_polls)
    polls_lists, general_polls = Poll.get_polls_list(request.user.student)  #
    if grade:
        if request.method == "POST":
            form = PollCombineForm(request.POST, polls=grouped_polls)
            if form.is_valid():
                unblindst = json.loads(request.POST.get('unblindst', ''))
                unblindt = json.loads(request.POST.get('unblindt', ''))
                connected_groups = connect_groups(grouped_polls, form)
                if connected_groups:
                    groups = reduce(list.__add__, connected_groups)
                else:
                    groups = []
                prepared_tickets = zip(groups, unblindt, unblindst)
                # final mark:
                for g, t, unblind in prepared_tickets:
                    secure_mark(request.user, g, t)
                errors, tickets_to_serve = get_valid_tickets(prepared_tickets)
                if errors:
                    message = u'Nie udało się pobrać następujących biletów:\n<ul>'
                    for poll, reason in errors:
                        message += u"<li>Ankieta: " + unicode(poll)
                        message += u"<br>Powód: "
                        message += unicode(reason)
                        message += u"</li>"
                    message += u"</ul>"
                    messages.error(request, SafeUnicode(message))
                data = {'tickets': to_plaintext(tickets_to_serve),
                        'grade': grade}

                if tickets_to_serve:
                    StudentGraded.objects.get_or_create(student=request.user.student,
                                                        semester=semester)

                return render(request, "grade/ticket_create/tickets_save.html", data)

        data = {'polls': polls_lists, 'grade': grade, 'general_polls': general_polls}
        return render(request, 'grade/ticket_create/connection_choice.html', data)
    else:
        messages.error(request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'grade/ticket_create/connection_choice.html', {'grade': grade})


@student_required
def keys_list(request):
    """
        Strona, z ktorej student moze pobrac klucze publiczne ankiet, ktore ma prawo wypelnic
    """
    polls = filter(lambda x: x.pk, Poll.get_all_polls_for_student(request.user.student))
    keys = PublicKey.objects.filter(poll_id__in=polls)
    return render(request, 'grade/ticket_create/keys_list.html', {'public_keys': keys, })


def sign_tickets(request):
    """
        Student przekazuje swoje kupony do podpisu kluczami prywatnymi przedmiotow
    """
    if request.method == 'POST':
        ticket_str = request.POST['tickets']
        tmp = ticket_str.split('**********************************')
        signatures = []
        try:
            tickets = list(map(convert_ticket_record, tmp))
            for ticket in tickets:
                poll_id = ticket[0]
                key = PrivateKey.objects.get(poll_id=poll_id)
                result = sign_ticket(ticket[1], key)
                signatures.append(Signature(poll_id, result))
                return render(request, 'grade/ticket_create/signed_tickets.html', {'signatures': signatures})
        except Exception:
            pass
    return render(request, 'grade/ticket_create/sign_tickets.html')


def create_voter_account(request):
    """
        Student przekazuje swoje klucze i otrzymuje w zamian tymczasowe konto do głosowania
    """
    if request.method == 'POST':
        pass

        return render(request, 'grade/ticket_create/create_voter_account.html')


def keys_generate(request):
    """
        Widok odpowiadajacy za generowanie kluczy RSA dla ankiet
    """
    if request.method == 'POST':
        # TODO check if the keys exist and delete them? (known problem in the system)
        generate_keys_for_polls()
    # count = cache.get('generated-keys', 0)
    # without_keys = Poll.count_polls_without_keys()
    data = {'progress_val': 50}
    return render(request, 'grade/ticket_create/keys_generate.html', data)
