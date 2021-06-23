from datetime import datetime
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.term import Term
from apps.schedule.models.event import Event
from django.contrib.auth.models import User

current_year = '2020/21'
next_year = '2021/22'
semester_type = 'z'

def run():
    ''' Filter all special reservation events that was in current_year '''
    reservations = Event.objects.filter(type=Event.TYPE_SPECIAL_RESERVATION, semester__year=current_year)
    for reservation in reservations:
        print(reservation)
        if input('Confirm (Y/n):') != 'n':
            event = Event()
            event.semester = Semester.objects.get(year=next_year, type=reservation.semester.type)
            event.title = reservation.title
            event.description = reservation.description
            event.type = Event.TYPE_SPECIAL_RESERVATION
            event.visible = True
            event.status = Event.STATUS_ACCEPTED
            event.author_id = User.objects.get(username='asm').id
            event.save()

            semester = reservation.semester
            term_days = semester.get_all_days_of_week(
                day_of_week=reservation.dayOfWeek, start_date=semester.lectures_beginning)

            for day in term_days:
                term = Term()
                term.event = event
                term.day = day
                term.start = reservation.start_time
                term.end = reservation.end_time
                term.room = reservation.classroom
                term.save()