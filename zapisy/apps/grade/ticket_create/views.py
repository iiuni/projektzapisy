import json
from functools import reduce
from apps.grade.poll.models import Poll
from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.models import PublicKey, PrivateKey
from apps.grade.ticket_create.utils import group_polls_by_course, generate_keys_for_polls, sign_ticket, \
    convert_ticket_record, generate_random_coupon, generate_blinding_factor, blind_ticket, connect_groups, \
    generate_keys, Signature
from apps.users.decorators import student_required
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.core.cache import cache
from apps.grade.ticket_create.forms import ContactForm, PollCombineForm


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
def ajax_get_rsa_keys_step1(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student(request.user.student)
            grouped_polls = group_polls_by_course(students_polls)
            form = PollCombineForm(request.POST, polls=grouped_polls)
            if form.is_valid():
                connected_groups = connect_groups(grouped_polls, form)
                tickets = [generate_keys(gs) for gs in connected_groups]
                message = json.dumps(tickets)
    return HttpResponse(message)


@student_required
def ajax_get_rsa_keys_step2(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student(request.user.student)
            groupped_polls = group_polls_by_course(students_polls)
            form = PollCombineForm(
                request.POST,
                polls=groupped_polls
            )
            if form.is_valid():
                ts = json.loads(request.POST['ts'])
                print('ts', ts)
                connected_groups = connect_groups(groupped_polls, form)
                groups = reduce(list.__add__, connected_groups)
                tickets = zip(groups, ts)
                signed = [(group, int(t), secure_signer_without_save(request.user, group, t))  # TODO continue here
                          for group, t in tickets]
                unblinds = [(str(ticket), unblind(group, ticket_signature))
                            for group, ticket, ticket_signature in signed]
                message = json.dumps(unblinds)
    return HttpResponse(message)


@student_required
def get_tickets(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        student_polls = Poll.get_all_polls_for_student(request.user.student)
        polls_list, general_polls = Poll.get_polls_list(request.user.student)
        if request.method == "POST":
            # grouped_polls = group_polls_by_course(student_polls)
            tickets = []
            # 1. generate random number m
            # 2. generate k gcd 1 with 512
            # 3. blind and sign
            # 4. send
            for poll in student_polls:
                m = generate_random_coupon()
                # k = generate_blinding_factor()
                # public_key = PublicKey.objects.get(pk=poll.pk).import_rsa_key()
                # private_key = PrivateKey.objects.get(pk=poll.pk).import_rsa_key()

            return render(request, 'grade/ticket_create/tickets_save.html', {'tickets': tickets, 'grade': grade})

        return render(request, 'grade/ticket_create/get_tickets.html',
                      {'polls': polls_list, 'grade': grade, 'general_polls': general_polls})
    else:
        messages.error(request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów")
        return render(request, 'grade/ticket_create/get_tickets.html', {'grade': grade})


@student_required
def keys_list(request):
    """
        Strona, z ktorej student moze pobrac klucze publiczne ankiet, ktore ma prawo wypelnic
    """
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    polls = [x.pk for x in Poll.get_all_polls_for_student(request.user.student)]
    keys = PublicKey.objects.filter(poll_id__in=polls)
    return render(request, 'grade/ticket_create/keys_list.html', {'public_keys': keys, 'grade': grade})


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
                return render(request, 'grade/ticket_create/signed_tickets.html',
                              {'signatures': signatures, 'grade': grade})
            except Exception as e:
                print('exception:' + str(e))
                messages.error(request, "Nie udało się podpisać kluczy")
        else:
            messages.info(request, "Nie podano kuponów do podpisu")
    return render(request, 'grade/ticket_create/sign_tickets.html', {'grade': grade})


def keys_generate(request):
    """
        Widok odpowiadajacy za generowanie kluczy RSA dla ankiet
    """
    if request.method == 'POST':
        generate_keys_for_polls()
    count = cache.get('generated-keys', 0)
    without_keys = Poll.count_polls_without_keys()
    return render(request, 'grade/ticket_create/keys_generate.html', {'progress_val': (count / without_keys) * 100})
