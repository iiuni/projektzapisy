# -*- coding: utf-8 -*-

from mailer.models import Message
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student, Program
from django.contrib.auth.models import User

studentsfile = 'dousuniecia.txt'

def process(line):
    line = line.strip()
    matricula = line
    try:
        student = Student.objects.get(matricula=matricula)
    except ObjectDoesNotExist:
        print(("***" + str(matricula) + " brak " + str(ects)))
        return
    print((student, student.status))
    # student.status = 0
    # student.save()
    
def run():
    file = open(studentsfile)
    for line in file:
        process(line)
