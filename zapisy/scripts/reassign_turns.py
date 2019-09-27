from apps.users.models import Student
from django.contrib.auth.models import User, Group
import random

turns = ['tura1', 'tura2', 'tura3']


def run():
    groups = Group.objects.filter(name__in=turns)
    # clear groups
    for group in groups:
        group.user_set.clear()
    # find all freshmen and shuffle the list
    students = list(Student.objects.filter(
        status=0,
        semestr=1,
        program__in=[4, 12, 14]))
    random.shuffle(students)
    # assign students to groups
    for i, student in enumerate(students):
        group = groups[i % groups.count()]
        group.user_set.add(student.user)
