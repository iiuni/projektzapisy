from datetime import datetime

from faker import Faker
from faker.providers import BaseProvider

from apps.enrollment.courses.models.semester import Semester

SEMESTER_YEAR_RANGE = 50


class SemesterYearProvider(BaseProvider):
    def semester_year(self):
        start_year = datetime.now().year
        end_year = start_year + SEMESTER_YEAR_RANGE
        f = Faker()
        while True:
            year = f.random_int(start_year, end_year)
            try:
                semester_year = Semester.get_semester_year_from_raw_year(year)
                Semester.objects.get(year=semester_year)
            except Semester.DoesNotExist:
                return year
