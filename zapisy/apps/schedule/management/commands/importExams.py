# -*- coding: utf-8 -*-


import datetime

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import Q

from apps.enrollment.courses.models import Semester, Freeday, ChangedDay, Classroom, Course
from apps.enrollment.courses.models import Term as T
from apps.schedule.models import Term, Event


class Command(BaseCommand):

    def handle(self, *args, **options):

        s4   = Classroom.objects.get(number='4')
        s5   = Classroom.objects.get(number='5')
        s7   = Classroom.objects.get(number='7')
        s107   = Classroom.objects.get(number='107')
        s108   = Classroom.objects.get(number='108')
        s110   = Classroom.objects.get(number='110')
        s25   = Classroom.objects.get(number='25')
        s141 = Classroom.objects.get(number='141')
        s119 = Classroom.objects.get(number='119')
        s105 = Classroom.objects.get(number='105')
        s104 = Classroom.objects.get(number='104')
        s103 = Classroom.objects.get(number='103')
        s139 = Classroom.objects.get(number='139')
        s140 = Classroom.objects.get(number='140')

        logika = Course.objects.get(id=3032)
        so     = Course.objects.get(id=3060)
        anal   = Course.objects.get(id=3017)
        eto    = Course.objects.get(id=3021)
        md     = Course.objects.get(id=3035)
        ask    = Course.objects.get(id=3020)
        numM   = Course.objects.get(id=3019)
        ewo    = Course.objects.get(id=3012)
        wdi    = Course.objects.get(id=3064)
        optymalizacja =  Course.objects.get(id=3040)

        wch = User.objects.get(id=55)
        egu = User.objects.get(id=15)
        zpl = User.objects.get(id=42)
        mpal = User.objects.get(id=66)
        gst = User.objects.get(id=45)
        tju = User.objects.get(id=17)
        kiero = User.objects.get(id=23)
        sle =  User.objects.get(id=30)
        wnuk =  User.objects.get(id=51)
        mwo =  User.objects.get(id=52)
        przemka =  User.objects.get(id=19)
        #s25


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = logika
        ev.author = wch
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s141
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s140
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s139
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s105
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s104
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s103
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s4
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s5
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s141
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=14, minute=0)
        newTerm.room = s140
        newTerm.save()



        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = eto
        ev.author = egu
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 2)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s25
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = so
        ev.author = zpl
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 1)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s25
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = anal
        ev.author = mpal
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 1)
        newTerm.start = datetime.time(hour=13, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s25
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = md
        ev.author = gst
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.place = 's. 13, Wielka Zachodnia'
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.place = s25
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = wdi
        ev.author = tju
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=15, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s141
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=15, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.place = 's. 13, Wielka Zachodnia'
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 4)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=18, minute=0)
        newTerm.place = 's. EM, Instytut Matematyczny'
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=9, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s25
        newTerm.save()



        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = ask
        ev.author = kiero
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 6)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 6)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s119
        newTerm.save()

        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = numM
        ev.author = sle
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 7)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 7)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.room = s141
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 7)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.place = 's. 13, Wielka Zachodnia'
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s141
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = ewo
        ev.author = wnuk
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 31)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 7)
        newTerm.start = datetime.time(hour=14, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.room = s119
        newTerm.save()


        ev = Event()
        ev.type   = '0'
        ev.visible = True
        ev.status  = '1'
        ev.course = optymalizacja
        ev.author = mwo
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 1)
        newTerm.start = datetime.time(hour=10, minute=0)
        newTerm.end = datetime.time(hour=13, minute=0)
        newTerm.room = s140
        newTerm.save()

        """
        Olimpiada
       """

        ev = Event()
        ev.type   = '2'
        ev.title = "Olimpiada informatyczna"
        ev.visible = False
        ev.status  = '1'
        ev.author = przemka
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=9, minute=0)
        newTerm.end = datetime.time(hour=11, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=15, minute=0)
        newTerm.end = datetime.time(hour=17, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=15, minute=0)
        newTerm.end = datetime.time(hour=17, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=15, minute=0)
        newTerm.end = datetime.time(hour=17, minute=0)
        newTerm.room = s119
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s105
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s105
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s105
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s105
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s104
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s104
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s104
        newTerm.save()




        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s107
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s107
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s107
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s107
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s107
        newTerm.save()


        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()



        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s110
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s110
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s110
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s110
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s110
        newTerm.save()



        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 11)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s7
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 12)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s7
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 13)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s7
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 14)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s7
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s7
        newTerm.save()


        """
        Egzamin licencjacki
        """

        ev = Event()
        ev.type   = '0'
        ev.title = "Egzamin licencjacki"
        ev.visible = True
        ev.status  = '1'
        ev.author = tju
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 5)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s140
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 6)
        newTerm.start = datetime.time(hour=8, minute=0)
        newTerm.end = datetime.time(hour=19, minute=0)
        newTerm.room = s140
        newTerm.save()

        ev = Event()
        ev.type   = '0'
        ev.title = "Egzamin wstępny na studia II stopnia"
        ev.visible = True
        ev.status  = '1'
        ev.author = gst
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 2, 15)
        newTerm.start = datetime.time(hour=9, minute=0)
        newTerm.end = datetime.time(hour=15, minute=0)
        newTerm.room = s119
        newTerm.save()

        """
                Zwykłe
       """

        ev = Event()
        ev.type   = '4'
        ev.title = "Chemia"
        ev.visible = False
        ev.status  = '1'
        ev.author_id = 1
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 12)
        newTerm.start = datetime.time(hour=13, minute=0)
        newTerm.end = datetime.time(hour=16, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day = datetime.datetime(2013, 1, 16)
        newTerm.start = datetime.time(hour=9, minute=0)
        newTerm.end = datetime.time(hour=12, minute=0)
        newTerm.room = s25
        newTerm.save()

        ev = Event()
        ev.type   = '4'
        ev.title = "Dzień Innowacyjnych firm"
        ev.visible = False
        ev.status  = '1'
        ev.author = przemka
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day   = datetime.datetime(2013, 1, 18)
        newTerm.start = datetime.time(hour=12, minute=0)
        newTerm.end   = datetime.time(hour=19, minute=0)
        newTerm.room = s25
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day   = datetime.datetime(2013, 1, 25)
        newTerm.start = datetime.time(hour=12, minute=0)
        newTerm.end   = datetime.time(hour=19, minute=0)
        newTerm.room = s25
        newTerm.save()

        ev = Event()
        ev.type   = '4'
        ev.title = "Tieto"
        ev.visible = False
        ev.status  = '1'
        ev.author_id = 1
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day   = datetime.datetime(2013, 1, 14)
        newTerm.start = datetime.time(hour=16, minute=0)
        newTerm.end   = datetime.time(hour=20, minute=0)
        newTerm.room = s107
        newTerm.save()

        ev = Event()
        ev.type   = '4'
        ev.title = 'Spotkanie w sprawie praktyk - AISEC'
        ev.visible = False
        ev.status  = '1'
        ev.author_id = 1
        ev.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day   = datetime.datetime(2013, 1, 16)
        newTerm.start = datetime.time(hour=17, minute=0)
        newTerm.end   = datetime.time(hour=19, minute=0)
        newTerm.room = s108
        newTerm.save()

        newTerm = Term()
        newTerm.event = ev
        newTerm.day   = datetime.datetime(2013, 1, 24)
        newTerm.start = datetime.time(hour=16, minute=0)
        newTerm.end   = datetime.time(hour=18, minute=0)
        newTerm.room = s110
        newTerm.save()
