from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student, Program
from django.contrib.auth.models import User

dyskretna_l = 'dyskretna2016.txt'
aisd_l = 'aisd2016.txt'
numerki_l = 'numerki2016.txt'


def process(line, t):
    line = line.split('|')
    matricula = int(line[0])

    try:
        student = Student.objects.get(matricula=matricula, status=0)
    except ObjectDoesNotExist:
        print("***" + str(matricula) + " brak")
        return
    if t == 'dyskretna_l':
        print(student, student.dyskretna_l)
        student.dyskretna_l = True
    if t == 'aisd_l':
        print(student, student.algorytmy_l)
        student.algorytmy_l = True
    if t == 'numerki_l':
        print(student, student.numeryczna_l)
        student.numeryczna_l = True
    student.save()


def run():
    file = open(dyskretna_l)
    for line in file:
        process(line, 'dyskretna_l')
    file = open(aisd_l)
    for line in file:
        process(line, 'aisd_l')
    file = open(numerki_l)
    for line in file:
        process(line, 'numerki_l')
