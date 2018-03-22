from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

ECTS_FILE = 'ects.txt'
students = {}


def process(line):
    matricula, ects, main, stopien, smieci = line.split()

    student = students.setdefault(matricula, {"I": 0, "II": -1, "III": -1})
    student[stopien] = max(int(ects), student[stopien])
    if stopien == 'II':
        student['I'] = max(180, student['I'])
    students[matricula] = student


def refresh(matricula, ects):
    ects_sum = ects['I'] + max(0, ects['II'])
    if ects_sum > 0:
        try:
            student = Student.objects.get(matricula=matricula, status=0)
        except ObjectDoesNotExist:
            print("***" + str(matricula) + " brak")
            return

        if not TESTING:
            print(student)
            print(student.ects)
            print(ects_sum)
            print("")
        student.ects = max(student.ects, ects_sum)
        student.save()


def import_ects(file):
    for line in file:
        process(line)

    for key, value in students.items():
        refresh(key, value)

# for running ectsimport.py from tests


def run_test(TEST_ECTS_FILE):
    global ECTS_FILE
    ECTS_FILE = TEST_ECTS_FILE
    run()


def run():
    file = open(ECTS_FILE)
    import_ects(file)
