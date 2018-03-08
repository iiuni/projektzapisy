
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student
timebonusfile = 'timebonus2016.txt'

def process(line):
    line = line.strip()
    indeks, bonus = line.split(',')
    try:
        student = Student.objects.get(matricula=indeks)
        student.records_opening_bonus_minutes = bonus
        student.save()
    except ObjectDoesNotExist:
        print(indeks + ': not found')


def run():
    file = open(timebonusfile)
    for line in file:
        process(line)
