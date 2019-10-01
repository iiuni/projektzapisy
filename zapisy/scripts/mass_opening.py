import datetime

from apps.enrollment.courses.models import Group
from apps.enrollment.records.models import GroupOpeningTimes
from apps.users.models import Student


def run():
    turns = ['tura1', 'tura2', 'tura3']
    opening_times = {
        'tura1': datetime.datetime(2019, 10, 1, 14, 0),
        'tura2': datetime.datetime(2019, 10, 1, 14, 30),
        'tura3': datetime.datetime(2019, 10, 1, 15, 0),
    }

    course_slugs = [
        'analiza-matematyczna-201920-zimowy', 'kurs-podstawowy-warsztat-informatyka-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-c-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-python-201920-zimowy',
        'wstep-do-informatyki-201920-zimowy'
    ]
    course_groups = Group.objects.filter(course__slug__in=course_slugs)

    for tura in turns:
        students_in_group = Student.objects.filter(user__groups__name=tura)
        time = opening_times.get(tura)

        for student in students_in_group:
            for group in course_groups:
                GroupOpeningTimes.objects.create(student=student, group=group, time=time)
