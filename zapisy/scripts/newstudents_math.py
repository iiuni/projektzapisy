from mailer.models import Message
from django.core.exceptions import ObjectDoesNotExist
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import T0Times, GroupOpeningTimes
from zapisy.apps.users.models import Student, Program
from django.contrib.auth.models import User
from django.db import connection
import datetime
import random

studentsfile = 'newstudents_math2016.txt'


def create_user(indeks, imie, nazwisko, mail, pswd):
    p = Program.objects.get(id=11)
    user = User.objects.create_user(username=indeks, email=mail, password=pswd)
    user.first_name = imie
    user.last_name = nazwisko
    user.save()
    s = Student.objects.create(user=user, matricula=indeks)
    s.semestr = 1
    s.program = p
    s.save()
    return user


def random_pass():
    alphabet = "abcdefghijkmnpqrstuvwxyz"
    upperalphabet = alphabet.upper()
    pw_len = 8
    pwlist = []

    for i in range(pw_len // 3):
        pwlist.append(alphabet[random.randrange(len(alphabet))])
        pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
        pwlist.append(str(random.randrange(8) + 2))
    for i in range(pw_len - len(pwlist)):
        pwlist.append(alphabet[random.randrange(len(alphabet))])

    random.shuffle(pwlist)
    pwstring = "".join(pwlist)

    return pwstring


def send_email(address):
    body = "Witaj,\n\nkonto zostało utworzone.\nlogin: nr indeksu\n\nHasło można uzyskać poprzez formularz:\nhttps://zapisy.ii.uni.wroc.pl/users/password-change/\n\nZespół zapisy.ii.uni.wroc.pl\n"
    subject = '[Zapisy] Nowe konto'
    Message.objects.create(
        to_address=address,
        from_address='zapisy@cs.uni.wroc.pl',
        subject=subject,
        message_body=body)


def process(line):
    line = line.strip()
    indeks, imie, nazwisko, mail, program = line.split(',')
    try:
        student = Student.objects.get(matricula=indeks)
    except ObjectDoesNotExist:
        haslo = random_pass()
        u = create_user(indeks, imie, nazwisko, mail, haslo)
        refresh_student_ECTS(u.student)
        send_email(mail)
        print(imie + ',' + nazwisko + ',' + indeks + ',' + haslo + ',' + program)
    else:
        print(str(indeks) + ': already exists')


def refresh_student_ECTS(student):
    cursor = connection.cursor()
    cursor.execute("SELECT points_refresh_for_student(%s);" % str(student.id))


def refresh_T0():
    semester = Semester.objects.filter(records_closing__gt=datetime.datetime.now())[0]
    T0Times.populate_t0(semester)
    GroupOpeningTimes.populate_opening_times(semester)
    return HttpResponseRedirect('/fereol_admin/courses')


def run():
    file = open(studentsfile)
    for line in file:
        process(line)
    print("accounts created, emails sent.")
    print("refreshing T0...")
    refresh_T0()
