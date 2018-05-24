import datetime

from django.core.management import BaseCommand
from django.db.models import Q

from apps.enrollment.courses.models.semester import Semester, Freeday, ChangedDay
from apps.enrollment.courses.models.term import Term as CoursesTerm
from apps.schedule.models import Term as ScheduleTerm, Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        semester = Semester.objects.get_next()
        Event.objects.filter(course__semester=semester, type=3).delete()
        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
            .values_list('day', flat=True)
        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(
            day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        terms = CoursesTerm.objects.filter(
            group__course__semester=semester).select_related(
            'group', 'group__course', 'group__course__entity')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning

        while day <= semester.lectures_ending:

            if day in freedays:
                day = day + datetime.timedelta(days=1)
                continue

            weekday = day.weekday()

            for d in changed:
                if d[0] == day:
                    weekday = int(d[1]) - 1
                    break

            days[weekday].append(day)

            day = day + datetime.timedelta(days=1)

        for t in terms:
            ev = Event.objects.get_or_create(
                group=t.group,
                course=t.group.course,
                title=t.group.course.entity.get_short_name(),
                type='3',
                visible=True,
                status='1',
                author=t.group.teacher.user)[0]

            for room in t.classrooms.all():
                for day in days[int(t.dayOfWeek) - 1]:
                    minute = t.start_time.minute
                    if minute == 0:
                        minute = 15
                    ScheduleTerm.objects.get_or_create(
                        event=ev,
                        day=day,
                        start=t.start_time,
                        end=t.end_time,
                        room=room)
