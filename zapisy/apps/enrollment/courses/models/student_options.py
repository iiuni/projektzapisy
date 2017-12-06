# -*- coding: utf-8 -*-

from django.db import models

from datetime import timedelta

import logging
logger = logging.getLogger()

class StudentOptions( models.Model ):
    """ Used for defining time bonus in records - for Student, Course. Student gets bonuses if voted for course. """
    course  = models.ForeignKey('Course', verbose_name = 'przedmiot')
    student = models.ForeignKey('users.Student', verbose_name = 'student')
    records_opening_bonus_minutes = models.IntegerField(default=0, verbose_name='Przyspieszenie otwarcia zapisów na ten przedmiot (minuty)')

    options_cache = {}

    @staticmethod
    def preload_cache(student, semester):
        '''
            Preloads cache with courses for certain student and semester.
        '''
        if not student.id in StudentOptions.options_cache:
            StudentOptions.options_cache[student.id] = {}
        if not semester.id in StudentOptions.options_cache[student.id]:
            StudentOptions.options_cache[student.id][semester.id] = {}
        for option in StudentOptions.objects.filter(course__semester=semester,\
            student=student).all().select_related('course'):
            StudentOptions.options_cache[student.id][semester.id]\
                [option.course.id] = option

    @staticmethod
    def get_cached(student, course):
        '''
            Returns StudentOption instance for student and course id.
            Doesn't make new query, if record is already cached.
        '''
        cache = StudentOptions.options_cache
        if not student.id in cache:
            cache[student.id] = {}
        if not course.semester.id in cache[student.id]: # miss
            cache[student.id][course.semester.id] = {}
        if not cache[student.id][course.semester.id]:
            options = StudentOptions.objects.filter(student=student)
            for o in options:
                cache[student.id][course.semester.id][o.course_id] = o

        if course.id in cache[student.id][course.semester.id]: # get
            return cache[student.id][course.semester.id][course.id]
        else: # not miss, but doesn't exists
            raise StudentOptions.DoesNotExist()

    def get_opening_delay_timedelta(self):
        """ returns records opening delay as timedelta """
        return timedelta(minutes=(-1)*self.records_opening_bonus_minutes+4320)

    class Meta:
        verbose_name = 'zależność przedmiot-student'
        verbose_name_plural = 'zależności przedmiot-student'
        unique_together = (('course', 'student'),)
        app_label = 'courses'

    def __str__(self):
        """ returns printable name of StudentOptions """
        return 'Przedmiot: %s, Student: %s ' % (self.course, self.student)
