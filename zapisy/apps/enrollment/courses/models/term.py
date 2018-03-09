from datetime import time, date

from django.db import models
from django.db.models import signals
from django.core.cache import cache as mcache
from zapisy import common
import logging

backup_logger = logging.getLogger('project.backup')

HOURS = [(str(hour), "%s.00" % hour) for hour in range(8, 23)]


class Term(models.Model):
    """terms of groups"""

    dayOfWeek  = models.CharField( max_length = 1, choices = common.DAYS_OF_WEEK, verbose_name = 'dzień tygodnia')
    start_time = models.TimeField(verbose_name = 'rozpoczęcie')
    end_time   = models.TimeField(verbose_name = 'zakończenie')
    classroom  = models.ForeignKey('Classroom', verbose_name='sala', null=True, blank=True, on_delete=models.CASCADE)
    group      = models.ForeignKey('Group', verbose_name='grupa', related_name='term', on_delete=models.CASCADE)
    classrooms = models.ManyToManyField('Classroom', related_name='new_classrooms', verbose_name='sale', blank=True)

    class Meta:
        #TO DO /pkacprzak/ add advanced constraint - example: start_time < end_time, any pair of terms can't overlap
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'
        ordering  = ['dayOfWeek']
        app_label = 'courses'


    @staticmethod
    def get_all_in_semester(semester, student=None, employee=None):
        filtered = Term.objects.filter(group__course__semester=semester).extra(
            select={'classrooms_as_string': """
                SELECT array_to_string(array(SELECT courses_classroom.number FROM courses_term_classrooms
                    JOIN courses_classroom
                    ON (courses_classroom.id = courses_term_classrooms.classroom_id)
                WHERE courses_term.id=courses_term_classrooms.term_id),',')"""})

        if student:
            from apps.enrollment.records.models import Record
            filtered = filtered.filter(group__id__in=\
                Record.get_student_enrolled_ids(student, semester))
            """
            inaczej można, powinno być jedno zapytanie mniej
            filtered.extra(where='"courses_group"."id" in' + (Record.enrolled.\
                        filter(student=student, group__course__semester=semester).\
                        values('group__pk', flat=True)).query.__str__() )

           """

        if employee:
            from apps.enrollment.records.models import Record
            filtered = filtered.filter(group__teacher=employee)

        return filtered.select_related('classroom', 'group', 'group__course', \
            'group__course__semester', 'group__course__entity',
            'group__course__entity__type', \
            'group__teacher', 'group__teacher__user').\
            prefetch_related('classrooms').\
            order_by('dayOfWeek', 'start_time').all()

    def day_in_zero_base(self):
        return int(self.dayOfWeek)-1

    def length_in_minutes(self):
        return (self.end_time.hour - self.start_time.hour)*60 + (self.end_time.minute - self.start_time.minute)

    def time_from_in_minutes(self):
        "Returns number of minutes from start of day (midnight) to term beggining"""
        return (self.start_time.hour)* 60 + (self.start_time.minute)

    def time_from(self):
        "Returns hourFrom in time format"""
        return self.start_time

    def time_to(self):
        "Returns hourTo in time format"""
        return self.end_time

    def _convert_string_to_time(self, str):
        hour, minute = [int(x) for x in str.split('.')]
        return time(hour=hour, minute=minute)

    def period_string(self):
        return "%s – %s" % (self.start_time.strftime("%H"), self.end_time.strftime("%H"))

    def get_dayOfWeek_display_short(self):
        return {
            '1': 'pn',
            '2': 'wt',
            '3': 'śr',
            '4': 'cz',
            '5': 'pt',
            '6': 'so',
            '7': 'nd',
        }[self.dayOfWeek]

    @staticmethod
    def get_day_of_week(date):
        return common.DAYS_OF_WEEK[date.weekday()][0]

    @staticmethod
    def get_python_day_of_week(day_of_week):
        return [x[0] for x in common.DAYS_OF_WEEK].index(day_of_week)

    @staticmethod
    def get_groups_terms(groups_ids):
        """
        Optimized query returning terms as string for group ids.
        """
        return [{'group_id':x.group_id,'term_as_string': "%s %s-%s (s.%s)" % (x.get_dayOfWeek_display_short(), x.start_time.strftime("%H:%M"), x.end_time.strftime("%H:%M"), x.classrooms_as_string)} for x in Term.objects.filter(group__in=groups_ids).extra(select={'classrooms_as_string': """
                                    SELECT array_to_string(array(SELECT courses_classroom.number FROM courses_term_classrooms
                                    JOIN courses_classroom
                                    ON (courses_classroom.id = courses_term_classrooms.classroom_id)
                                    WHERE courses_term.id=courses_term_classrooms.term_id),',')"""})]

    def numbers(self):
        if not self.id:
            return ''

        if hasattr(self, 'classrooms_as_string'):
            return self.classrooms_as_string
        classrooms = self.classrooms.all()
        if len(classrooms) > 0:
            classrooms = ' (s.' + ', '.join([x.number for x in classrooms]) + ')'
        else:
            classrooms = ''

        return classrooms

    @classmethod
    def get_terms_for_semester(cls, semester, day=None, classrooms=None, start_time=None, end_time=None):
        """
        A versatile function returning Terms. day is either datetime.date or string

        :param semester: enrollment.courses.model.Semester
        :param day: common.DAYS_OF_WEEK or datetime.date
        """
        from .semester import ChangedDay, Freeday
        query = cls.objects.filter(group__course__semester=semester)

        if day is None:
            pass
        else:
            if isinstance(day, date):
                if Freeday.is_free(day):
                    return cls.objects.none()
                day_of_week = ChangedDay.get_day_of_week(day)
            else:
                day_of_week = day
            query = query.filter(dayOfWeek=day_of_week)

        if classrooms:
            query = query.filter(classrooms__in=classrooms)

        if start_time and end_time:
            query = query.filter(start_time__lt=end_time, end_time__gt=start_time)

        return query.select_related('group__course')

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'group': self.group.pk,
            'classroom': self.classrooms_as_string,
            'day': int(self.dayOfWeek),
            'start_time': ("%d:%d" % (self.start_time.hour, self.start_time.minute)),
            'end_time': ("%d:%d" % (self.end_time.hour, self.end_time.minute)),
        }

    def __str__(self):
        """
        N query problem with self.classrooms.all(). If you want to optimize, use Term.get_groups_terms.
        """
        classrooms = self.numbers()
        return "%s %s-%s%s" % (self.get_dayOfWeek_display_short(), self.start_time.strftime("%H:%M"), self.end_time.strftime("%H:%M"), classrooms)

def log_edit_term(sender, instance, **kwargs):
    return
    try:
        term = instance
        old_term = Term.objects.get(id=term.id)
        string = [old_term.dayOfWeek,str(old_term.start_time),str(old_term.end_time)]
        if old_term.classroom:
            string.append(old_term.classroom.number)
        string = '-'.join(string)
        old_term_format = string

        newstring = [term.dayOfWeek,str(term.start_time),str(term.end_time)]
        if term.classroom:
            newstring.append(term.classroom.number)

        term_format = '-'.join(newstring)
        message = '[09] term for group {} has been updated from {} to {}'.format(
            term.group.id, old_term_format, term_format,
        )
        backup_logger.info(message)
    except Term.DoesNotExist:
        pass

def log_add_term(sender, instance, created, **kwargs):
    return
    term = instance
    if term.classroom and hasattr(term.classroom, "number"):
        number = term.classroom.number
    else:
        number = ''
    term_format = '-'.join([term.dayOfWeek,str(term.start_time),str(term.end_time),number])
    if created:
        message = '[08] term {} for group {} has been created'.format(
            term_format, term.group.id,
        )
        backup_logger.info(message)

def log_delete_term(sender, instance, **kwargs):
    return
    term = instance
    words = [term.dayOfWeek,str(term.start_time),str(term.end_time)]
    if term.classroom:
        words += term.classroom.number
    term_format = '-'.join(words)
    backup_logger.info('[10] term {} for group {} has been deleted'.format(
        term_format, term.group.id
    ))

signals.pre_save.connect(log_edit_term, sender=Term)
signals.post_save.connect(log_add_term, sender=Term)
signals.pre_delete.connect(log_delete_term, sender=Term)

def recache(sender, **kwargs):
    mcache.clear()

signals.post_save.connect(recache, sender=Term)
signals.post_delete.connect(recache, sender=Term)
