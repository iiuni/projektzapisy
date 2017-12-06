# -*- coding: utf-8 -*-

from mailer.models import Message
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student, Program
from django.contrib.auth.models import User

studentsfile = 'studentsII2016.txt'

def process(line):
    line = line.split()
    ptype = int(line[0])
    nazwisko = line[1]
    imie = line[2]
    try:
        if nazwisko == 'Pietrzak':
            u = User.objects.get(username='264573')
        else:
            u = User.objects.get(last_name = nazwisko, first_name = imie)
    except ObjectDoesNotExist:
        print("***" + str(line) + " brak")
        return
    print((u.get_full_name()))
    u.student.program = Program.objects.get(id=ptype)
    if ptype == 1:
        u.student.ects = 180
    else:
        u.student.ects = 210
    u.student.status = 0
    #u.student.save()

    address = u.email
    if (address):
        body = "Witaj na studiach II stopnia, \n\nw Systemie Zapisów zaktualizowano Twoje punkty ECTS i wygenerowano nowy czas otwarcia. \n\nZespół zapisy.ii.uni.wroc.pl\n"
        subject = '[ZAPISY] Studia II stopnia - nowe T0'
        print('a')
        #Message.objects.create(to_address=address, from_address='zapisy@cs.uni.wroc.pl', subject=subject, message_body=body)

def run():
    file = open(studentsfile)
    for line in file:
        process(line)
