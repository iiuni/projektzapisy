from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models import Course, CourseEntity
from apps.offer.vote.models import SystemState
from apps.offer.vote.models.single_vote import SingleVote

enrollfile = 'enroll2016.txt'


def process(line):
    line = line.strip()
    indeks, group_id = line.split(',')
    try:
        student = Student.objects.get(matricula=indeks)
        ss = SystemState.objects.get(id=11)
        ce = CourseEntity.objects.get(id=842)
        cc = Course.objects.get(id=3568)
        sv = SingleVote.objects.get_or_create(
            student=student,
            entity=ce,
            course=cc,
            state=ss,
            value=3,
            correction=3,
            free_vote=True)
        # g = Group.objects.get(id=group_id)
        # g.enroll_student(student)
    except ObjectDoesNotExist:
        print(indeks + ' or ' + srt(group_id) + ' not found')


def run():
    file = open(enrollfile)
    for line in file:
        process(line)
