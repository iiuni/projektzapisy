from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.specialreservation import SpecialReservation
from django.contrib.auth.models import User

current_year = '2018/19'
next_year = '2019/20'


def run():
    author_id = User.objects.get(username='asm').id
    reservations = SpecialReservation.objects.filter(
        semester__year=current_year)
    for reservation in reservations:
        print(reservation)
        if input('Confirm (Y/n):') != 'n':
            new_reservation = SpecialReservation(
                semester=Semester.objects.get(
                    year=next_year,
                    type=reservation.semester.type),
                title=reservation.title,
                classroom=reservation.classroom,
                dayOfWeek=reservation.dayOfWeek,
                start_time=reservation.start_time,
                end_time=reservation.end_time)
            new_reservation.save(author_id)
