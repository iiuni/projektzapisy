from apps.users.models import Student
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mass_mail

studentsfile = 'h.txt'
from_address = 'zapisy@cs.uni.wroc.pl'
subject = '[Zapisy] Hasło do pracowni komputerowych'


def run():
    file = open(studentsfile)
    messages = []
    for line in file:
        line = line.strip()
        matricula, password = line.split(' ')
        try:
            student = Student.objects.get(matricula=matricula)
        except ObjectDoesNotExist:
            print(matricula, password)
        else:
            first_name = student.user.first_name
            to_address = student.user.email
            body = f"""Witaj {first_name},

przypisano Ci hasło początkowe do systemów w pracowniach komputerowych:

{password}

Zespół zapisy.ii.uni.wroc.pl
---
Wiadomość wygenerowana automatycznie, prosimy na nią nie odpowiadać."""
            messages.append((subject, body, from_address, [to_address]))
    delivered_count = send_mass_mail(messages, fail_silently=False)
    print(delivered_count)
