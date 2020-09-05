from datetime import datetime

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester


class SemesterObjectMother():

    @staticmethod
    def winter_semester_2015_16():
        """Records opening and closing dates are made up."""
        semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            year='2015/16',
            records_opening=datetime(2015, 9, 20),
            records_closing=datetime(2015, 10, 14),
            lectures_beginning=datetime(2015, 10, 1),
            lectures_ending=datetime(2016, 2, 3),
            semester_beginning=datetime(2015, 10, 1),
            semester_ending=datetime(2016, 2, 21),
            records_ects_limit_abolition=datetime(2015, 10, 1),
            is_grade_active=False
        )
        semester.full_clean()
        return semester

    @staticmethod
    def summer_semester_2015_16():
        """Records opening and closing dates are made up."""
        semester = Semester(
            visible=True,
            type=Semester.TYPE_SUMMER,
            year='2015/16',
            records_opening=datetime(2016, 2, 24),
            records_closing=datetime(2016, 3, 14),
            lectures_beginning=datetime(2016, 2, 22),
            lectures_ending=datetime(2016, 6, 16),
            semester_beginning=datetime(2016, 2, 22),
            semester_ending=datetime(2016, 9, 10),
            records_ects_limit_abolition=datetime(2016, 3, 1),
            is_grade_active=False
        )
        semester.full_clean()
        return semester


class ClassroomObjectMother():

    @staticmethod
    def room110():
        room = Classroom(
            type=3,
            description='Pracownia z najszybszymi komputerami w instytucie',
            number='110',
            building='Instytut Informatyki',
            capacity=20,
            floor=1,
            can_reserve=True
        )
        room.full_clean()
        return room

    @staticmethod
    def room104():
        room = Classroom(
            type=1,
            description='Sala cwiczeniowa',
            number='104',
            building='Instytut Informatyki',
            capacity=32,
            floor=1,
            can_reserve=True
        )
        room.full_clean()
        return room
