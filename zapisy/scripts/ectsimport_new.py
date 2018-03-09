
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student

ECTS_FILE = 'ects2016.txt'

def deactivate_all():
    students = Student.objects.all()
    for s in students:
        s.status = 1
        s.save()

def process(line):
    line = line.strip()
    matricula, ects = line.split('|')
    ects = int(ects)
    try:
        student = Student.objects.get(matricula=matricula)
    except ObjectDoesNotExist:
        print("***" + str(matricula) + " brak " + str(ects))
        return
    print(student, student.ects, ects)
    student.ects = max(student.ects, ects)
    student.status = 0
    student.save()

def import_ects(file):
    for line in file:
        process(line)

def run():
    deactivate_all()
    file = open(ECTS_FILE)
    import_ects(file)
