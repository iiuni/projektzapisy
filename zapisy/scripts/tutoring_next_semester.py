from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models import Course, CourseEntity, Semester
from apps.enrollment.records.models import Record
from apps.offer.vote.models import SystemState


def run():
    ent = CourseEntity.objects.get(name_pl="Kształtowanie ścieżki akademicko-zawodowej")
    sem = Semester.get_current_semester()
    sem2 = sem.get_next_by_semester_beginning()
    course1 = Course.objects.get(semester=sem, entity=ent)
    course2 = Course.objects.get(semester=sem2, entity=ent)
    groups1 = course1.groups.filter().order_by('teacher')
    groups2 = course2.groups.filter().order_by('teacher')
    for i in range(len(groups1)):
        g1 = groups1[i]
        g2 = groups2[i]
        print(g1)
        print(g2)
        for s in Record.get_students_in_group(g1):
            if s.status == 0:
                g2.add_student(s)
                print(g2, s, s.isim)
