from zapisy.apps.users.models import Student
from apps.enrollment.courses.models.group import Group


def run():
    group_id_first_year = 13700
    group_id_rest = 13701
    isim_id = 14
    g1 = Group.objects.get(id=group_id_first_year)
    g2 = Group.objects.get(id=group_id_rest)
    sisim = Student.objects.filter(program_id=isim_id)
    c1 = 0
    c2 = 0
    for s in sisim:
        if s.ects == 0:
            g1.enroll_student(s)
            c1 += 1
        else:
            g2.enroll_student(s)
            c2 += 1
    print("First year isim enrolled: " + str(c1))
    print("Second year isim enrolled: " + str(c2))
