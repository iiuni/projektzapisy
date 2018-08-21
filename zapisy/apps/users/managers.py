from django.db import models
from django.db.models.aggregates import Min
from django.db.models import QuerySet
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.models import Student
    from apps.enrollment.courses.models import Semester


class GettersManager(models.Manager):

    def filter_with_t0(self, *args: Any, **kwargs: Any) -> QuerySet:
        return self.get_queryset().filter(*args, **kwargs).only('user__first_name', 'user__last_name',
                                                                'matricula', 'ects').annotate(t0_min=Min('opening_times__opening_time'))

    def get_list_full_info(self, begin: str='All') -> QuerySet:
        def next_char(begin):
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)

        if begin == 'Z':
            return self.filter_with_t0(status=0, user__last_name__gte=begin).\
                select_related('user').order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return self.filter_with_t0(status=0).\
                select_related('user').order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return self.filter_with_t0(status=0, user__last_name__range=(begin, end)).\
                select_related('user').order_by('user__last_name', 'user__first_name')
