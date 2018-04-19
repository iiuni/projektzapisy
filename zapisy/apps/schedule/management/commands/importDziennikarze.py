import datetime

from django.core.management import BaseCommand
from django.db.models import Q

from apps.enrollment.courses.models import Semester, Freeday, ChangedDay, Classroom
from apps.enrollment.courses.models.term import Term as T
from apps.schedule.models import Term, Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        semester = Semester.get_current_semester()

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
            .values_list('day', flat=True)
        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(
            day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning

        s4 = Classroom.objects.get(number='4')
        s5 = Classroom.objects.get(number='5')
        s25 = Classroom.objects.get(number='25')
        s141 = Classroom.objects.get(number='141')
        s139 = Classroom.objects.get(number='139')
        s140 = Classroom.objects.get(number='140')
        s103 = Classroom.objects.get(number='103')
        s104 = Classroom.objects.get(number='104')
        s105 = Classroom.objects.get(number='105')
        s108 = Classroom.objects.get(number='108')
        s110 = Classroom.objects.get(number='110')
        s119 = Classroom.objects.get(number='119')
        s237 = Classroom.objects.get(number='237')
        s310 = Classroom.objects.get(number='310')

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

        def create_event(title, visible=True):
            ev = Event()
            ev.title = title
            ev.type = '4'
            ev.visible = visible
            ev.status = '1'
            ev.author_id = 1
            ev.save()

            return ev

        def create_term(event, day, start, end, room, minutes_start=0, minutes_end=0):
            newTerm = Term()
            newTerm.event = event
            newTerm.day = day
            newTerm.start = datetime.time(hour=start, minute=minutes_start)
            newTerm.end = datetime.time(hour=end, minute=minutes_end)
            newTerm.room = room
            newTerm.save()

        for d in days[4]:  # piatek
            ev = create_event('Kolokwia')
            create_term(ev, d, 14, 16, s25)

            ev = create_event('Jezyk Angielski')
            create_term(ev, d, 12, 15, s4)

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 15, 20, s141)
            create_term(ev, d, 15, 20, s140)
            create_term(ev, d, 15, 20, s139)
            create_term(ev, d, 15, 20, s103)
            create_term(ev, d, 15, 20, s104)
            create_term(ev, d, 15, 20, s4)
            create_term(ev, d, 15, 20, s5)

            ev = create_event('SEMINARIUM ZJP')
            create_term(ev, d, 13, 15, s105)

        for d in days[5]:  # sobota

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 9, 18, s141)
            create_term(ev, d, 9, 18, s140)
            create_term(ev, d, 9, 18, s139)
            create_term(ev, d, 9, 18, s103)
            create_term(ev, d, 9, 18, s104)
            create_term(ev, d, 9, 18, s5)
            create_term(ev, d, 9, 18, s4)

        for d in days[6]:  # niedziela

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 9, 18, s141)
            create_term(ev, d, 9, 18, s140)
            create_term(ev, d, 9, 18, s139)
            create_term(ev, d, 9, 18, s103)
            create_term(ev, d, 9, 18, s104)
            create_term(ev, d, 9, 18, s5)
            create_term(ev, d, 9, 18, s4)

        for d in days[0]:  # poniedzialke

            ev = create_event('Jezyk Angielski')
            create_term(ev, d, 8, 12, s4)

            ev = create_event('INSTYTUT MATEMATYCZNY')
            create_term(ev, d, 10, 12, s104)

        for d in days[1]:  # wtorek
            ev = create_event('JUG')
            create_term(ev, d, 18, 21, s25, minutes_start=30)

            ev = create_event('SEMINARIUM ZMN')
            create_term(ev, d, 14, 16, s104)
            create_term(ev, d, 14, 16, s237)

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 12, 14, s4)

            ev = create_event('JUG')
            create_term(ev, d, 18, 21, s25, 30)

            ev = create_event('Grupa .NET')
            create_term(ev, d, 18, 20, s119)

        for d in days[2]:  # sroda

            ev = create_event('SEMINARIUM PGK')
            create_term(ev, d, 12, 14, s105)

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 10, 12, s4)

        for d in days[3]:  # czwartek

            ev = create_event('SEMINARIUM PIO')
            create_term(ev, d, 16, 18, s237)

            ev = create_event('SEMINARIUM ZZOIA')
            create_term(ev, d, 12, 14, s119)

            ev = create_event('SEMINARIUM INSTYTUTOWE')
            create_term(ev, d, 14, 16, s119)

            ev = create_event('INSTYTUT DZIENNIKARSTWA')
            create_term(ev, d, 8, 10, s4)
            create_term(ev, d, 12, 14, s4)
            create_term(ev, d, 16, 20, s5)
