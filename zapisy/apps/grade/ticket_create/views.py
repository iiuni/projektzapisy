from apps.grade.poll.models import Poll
from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.models import PublicKey, PrivateKey
from apps.grade.ticket_create.utils import generate_keys_for_polls, sign_ticket, convert_ticket_record, Signature
from apps.users.decorators import student_required
from django.shortcuts import render
from django.contrib import messages


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
        # TODO check if the keys exist and delete them? (known problem in the system)
        generate_keys_for_polls()
    data = {'progress_val': 50}
    return render(request, 'grade/ticket_create/keys_generate.html', data)
