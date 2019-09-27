from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.courses.models.group import Group
from apps.users.models import Student
import random

group_ids = [15694, 15696, 15697]


def run():
    # find all freshmen and shuffle the list
    students = Student.objects.filter(
        status=0,
        semestr=1,
        program__in=[4, 12]).order_by('?')
    # assign students to groups
    for i, student in enumerate(students):
        group_id = group_ids[i % len(group_ids)]
        Record.objects.create(
            group_id=group_id,
            student=student,
            status=RecordStatus.ENROLLED)
