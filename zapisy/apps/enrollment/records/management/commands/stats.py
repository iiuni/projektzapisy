from optparse import make_option

from django.core.management.base import BaseCommand

from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record
from apps.users.models import Student


class Command(BaseCommand):
    args = ''
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--person',
                    action='store_true',
                    dest='person',
                    default=False,
                    help='list by person'),
        make_option('--group',
                    action='store_true',
                    dest='group',
                    default=False,
                    help='list term by group'),
        make_option('--type',
                    action='store_true',
                    dest='type',
                    default=False,
                    help='list group by type'),
    )

    def handle(self, *args, **options):
        semester = Semester.get_default_semester()
        if options['person']:
            students = Student.objects.filter(status=0)
            for student in students:
                records = Record.enrolled.filter(student=student, group__course__semester=semester)
                for r in records:
                    print(str(student.id) + ' ' + str(r.group_id))

        if options['group']:
            groups = Group.objects.filter(course__semester=semester)
            for g in groups:
                for t in g.term.all():
                    print(str(g.id) + ' ' + str(t))

        if options['type']:
            groups = Group.objects.filter(course__semester=semester)
            for g in groups:
                print(str(g.id) + ' ' + g.get_type_display())
