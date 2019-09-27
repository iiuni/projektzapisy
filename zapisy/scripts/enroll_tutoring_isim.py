from apps.users.models import Student
from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models.records import Record, RecordStatus


def enroll(group, student):
    Record.object.create(
        group=group,
        student=student,
        status=RecordStatus.ENROLLED)


def run():
    group_id_first_year = 15699
    group_id_rest = 15698
    isim_id = 14
    g1 = Group.objects.get(id=group_id_first_year)
    g2 = Group.objects.get(id=group_id_rest)
    sisim = Student.objects.filter(program_id=isim_id)
    c1 = 0
    c2 = 0
    for s in sisim:
        if s.ects == 0:
            enroll(g1, s)
            c1 += 1
        else:
            enroll(g2, s)
            c2 += 1
    print("First year isim enrolled: " + str(c1))
    print("Other year isim enrolled: " + str(c2))
