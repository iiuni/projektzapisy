import datetime

from apps.enrollment.courses.models import Group
from apps.enrollment.records.models import GroupOpeningTimes
from apps.users.models import Student


def run():
    course_slugs = [
        'analiza-matematyczna-201920-zimowy', 'kurs-podstawowy-warsztat-informatyka-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-c-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-python-201920-zimowy',
        'wstep-do-informatyki-201920-zimowy'
    ]
    course_groups = Group.objects.filter(course__slug__in=course_slugs)

    student = Student.objects.get(matricula='314308')
    time = datetime.datetime(2019, 10, 1, 15, 0)

    for group in course_groups:
        GroupOpeningTimes.objects.create(student=student, group=group, time=time)
