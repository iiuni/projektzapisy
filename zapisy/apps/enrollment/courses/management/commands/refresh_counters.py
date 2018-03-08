from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models import Semester, Group
from apps.enrollment.records.models import Record, Queue
from apps.users.models import Student
from apps.enrollment.records.utils import run_rearanged

class Command(BaseCommand):
    args = ''
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--test',
                    action='store_true',
                    dest='test',
                    default=False,
                    help='test run to detect invalid enrolled / queued counters'),
        make_option('--semester',
                    action='store',
                    dest='semester',
                    type='int',
                    default=0,
                    help='Select semester id to run fixing on. Default current semester.')
    )

    def handle(self, *args, **options):
        semester = None
        print(options['semester'])
        if options['semester'] == 0:
            semester = Semester.get_default_semester()
        else:
            semester = Semester.objects.get(pk=int(options['semester']))
        groups = Group.objects.filter(course__semester=semester)
        enrolled_errors = 0
        queued_errors = 0
        for group in groups:
            enrolled_errors += self.refresh_enrolled(group, options['test'])
            queued_errors += self.refresh_queued(group, options['test'])
        print("Enrolled errors: ", enrolled_errors)
        print("Queued errors: ", queued_errors)
        print("No of Groups checked: ", len(groups))

    def refresh_enrolled(self, group, test):
        records = Record.objects.filter(group=group, status=Record.STATUS_ENROLLED).prefetch_related('student')
        error_cnt = 0

        enrolled_cnt = len(records)
        if group.enrolled != enrolled_cnt:
            old_enrolled_cnt = group.enrolled
            if not test:
                group.enrolled = enrolled_cnt
                group.save()
                if old_enrolled_cnt > enrolled_cnt:
                    for _ in range(old_enrolled_cnt - enrolled_cnt):
                        run_rearanged(None, group)
            print("enrolled counter error for group:", group)
            print("previous value: ", old_enrolled_cnt, ", new value: ", enrolled_cnt)
            if old_enrolled_cnt > enrolled_cnt:
                print("(runned rearanged ",old_enrolled_cnt - enrolled_cnt," times)")
            error_cnt += 1

        enrolled_zam_cnt = len([x for x in records if x.student.is_zamawiany()])
        if group.enrolled_zam != enrolled_zam_cnt:
            old_enrolled_zam_cnt = group.enrolled_zam
            if not test:
                group.enrolled_zam = enrolled_zam_cnt
                group.save()
            print("enrolled_zam counter error for group", group)
            print("previous value: ", old_enrolled_zam_cnt, ", new value: ", enrolled_zam_cnt)
            error_cnt += 1

        enrolled_zam2012_cnt = len([x for x in records if x.student.is_zamawiany2012()])
        if group.enrolled_zam2012 != enrolled_zam2012_cnt:
            old_enrolled_zam2012_cnt = group.enrolled_zam2012
            if not test:
                group.enrolled_zam2012 = enrolled_zam2012_cnt
                group.save()
            print("enrolled_zam2012 counter error for group", group)
            print("previous value: ", old_enrolled_zam2012_cnt, ", new value: ", enrolled_zam2012_cnt)
            error_cnt += 1

        enrolled_isim_cnt = len([x for x in records if x.student.isim])
        if group.enrolled_isim != enrolled_isim_cnt:
            old_enrolled_isim_cnt = group.enrolled_isim
            if not test:
                group.enrolled_isim = enrolled_isim_cnt
                group.save()
            print("enrolled_isim counter error for group", group)
            print("previous value: ", old_enrolled_isim_cnt, ", new value: ", enrolled_isim_cnt)
            error_cnt += 1

        return error_cnt


    def refresh_queued(self, group, test):
        queued_cnt = Queue.objects.filter(group=group, deleted=False).count()
        if(group.queued != queued_cnt):
            old_queued_cnt = group.queued
            if not test:
                group.queued = queued_cnt
                group.save()
            print("queued counter fixed for group:", group)
            print("previous value: ", old_queued_cnt, ", new value: ", queued_cnt)
            return 1
        return 0
