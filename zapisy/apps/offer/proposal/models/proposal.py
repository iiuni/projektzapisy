# -*- coding: utf-8 -*-

"""
    Proposal of course
"""

from datetime import datetime

from django.db                  import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from apps.offer.proposal.exceptions import NonStudentException, NonEmployeeException

import re


from apps.users.models                       import Employee, Student
from django.template.defaultfilters import slugify

class NoRemovedManager(models.Manager):
    def get_query_set(self):
        return super(NoRemovedManager, self).get_query_set().filter(deleted=False)

class FiltredManager(models.Manager):
    def get_query_set(self):
        return super(FiltredManager, self).get_query_set().filter(deleted=False, for_student=True)

# TO BE DELETED
class Przedmiot(models.Model):
    kod_uz = models.IntegerField()
    nazwa = models.TextField()
    name = models.TextField()
    punkty = models.IntegerField()
    rodzaj = models.IntegerField()
    liczba_godzin = models.TextField(null=True, blank=True)
    egzamin = models.BooleanField()
    angielski = models.BooleanField()
    aktualny = models.BooleanField()
    strona_domowa = models.TextField()
    wymagania = models.TextField()
    program = models.TextField()
    opis = models.TextField()
    literatura = models.TextField()
    semestr  = models.IntegerField()
    punkty2007  = models.IntegerField()
    rodzaj2007  = models.IntegerField()

    class Meta:
        app_label = 'proposal'


# TO BE DELETED
class Proposal( models.Model ):
    """
        Proposal of course
    """
    from apps.offer.proposal.models.proposal_description import ProposalDescription

    PROPOSAL_STATUS = [(0, 'Propozycja'), (1, 'Oferta'), (2, 'Głosowanie')]
    SEMESTER_LIST   = [('u', 'Nieustolony'), ('w', 'Zima'), ('s', 'Lato')]
#    name     = models.CharField(max_length = 255,
#                                 unique = True,
#                                verbose_name = 'nazwa przedmiotu' )
#    slug     = models.SlugField(max_length = 255,
#                                 unique = True,
#                                 verbose_name='odnośnik' )
##    fans     = models.ManyToManyField('users.Student',
##                                      verbose_name='poszli by na to',
##                                        blank=True)
##    teachers = models.ManyToManyField('users.Employee',
##                                      blank=True,
##                                      related_name='proposal_teachers_related',
##                                      verbose_name='poprowadziliby to')
##    helpers  = models.ManyToManyField('users.Employee',
##                                      blank=True,
##                                      related_name='proposal_helpers_related',
##                                      verbose_name='pomogliby poprowadzić to')
#    owner    = models.ForeignKey(User,
#                                 related_name='wlasciciel',
#                                 verbose_name='wlasciciel',
#                                 null = True, blank=True)
#    hidden   = models.BooleanField(verbose_name='ukryta',
#                                   default=False)
#    deleted  = models.BooleanField(default=False,
#                                   verbose_name="usuniety")
#    status   = models.IntegerField(choices=PROPOSAL_STATUS,
#                                   default=0,
#                                   verbose_name="status przedmiotu",
#                                    help_text=u'Propozycja - widoczna jedynie dla autora i administratora<br/>' \
#                                              u'Oferta - przedmiot widoczny w ofercie, nieobecny w głosowaniu<br/>' \
#                                              u'Głosowanie - przedmiot widoczny zarówno w ofercie jak i głosowaniu'
#                                )
#    semester = models.CharField(choices=SEMESTER_LIST,
#                                default='b',
#                                max_length=1,
#                                verbose_name="przypisane do semestru")
#
##    for_student = models.BooleanField(default=True,
##                                      verbose_name='widoczna dla studentów')
#
#    student = models.BooleanField(default=False,
#                                    verbose_name="propozycja studenta")
##    description = models.ForeignKey(ProposalDescription,
##                                    verbose_name=''
##                                    related_name='proposals_set')
#
#    description = models.TextField(verbose_name='opis')
#
#    requirements = models.TextField( verbose_name = 'wymagania' )
#    comments     = models.TextField( blank = True, null=True,
#                                     verbose_name = 'uwagi' )
#    date         = models.DateTimeField(auto_now=True,
#                                        verbose_name = 'data dodania')
#
#    deleted      = models.BooleanField(default=False,
#                                       verbose_name='usunięty')
#    exam         = models.BooleanField(choices=((False, 'Nie'), (True, 'Tak')),
#                                       default=False,
#                                       verbose_name='z egzaminem')
#    english      = models.BooleanField(default=False,
#                                       verbose_name=u'możliwe zajęcia po angielsku')
#    web_page     = models.URLField( verbose_name = 'Strona WWW przedmiotu',
#                                verify_exists= True,
#								blank        = True,
#                                null         = True )
#    course_type         = models.ForeignKey('courses.Type',
#                                verbose_name= u'Typ',
#                                related_name = 'descriptionstypes')


    objects   = models.Manager()
    filtred   = FiltredManager()
    noremoved = NoRemovedManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Proposal, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'proposal'
#        ordering = ['name']
        permissions = (
            ("can_create_offer", u"Może tworzyć ofertę dydaktyczną"),
            ("can_delete_proposal", u"Może usuwać propozycje"),
        )


    def entry_date(self):
        """
            Get date of first "description" - when this proposal was entered.
        """
        return self.description.date

    def is_new(self):
        """
            Is true, when proposal is newer than half of year.
        """
        diff = (datetime.now() - self.entry_date())
        return diff.days < 30 * 6

    def is_in_group(self, user, group):
        """
            Is true when user is in group.
            Possible groups:
            fans
            teachers
            helpers
        """

        try:
            if group == 'fans':
                if self.fans.get(id=user.student.id):
                    return True
                return False
            elif group == 'teachers':
                if self.teachers.get(id = user.employee.id):
                    return True
                return False
            elif group == 'helpers':
                if self.helpers.get(id = user.employee.id):
                    return True
                return False

        except Student.DoesNotExist:
            return False
        except Employee.DoesNotExist:
            return False            

    def add_user_to_group(self, user, group):
        """
            Add user to group
            Possible group:
            fans
            teachers
            helpers
        """
        try:
            if group == 'fans':
                field = self.fans
                person = user.student
            elif group == 'teachers':
                field = self.teachers
                person = user.employee
            elif group == 'helpers':
                field = self.helpers
                person = user.employee
            field.add(person)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()
        except Employee.DoesNotExist:
            raise NonEmployeeException()

    def delete_user_from_group(self, user, group):
        """
            Delete user from group
            Possible group:
            fans
            teachers
            helpers
        """
        try:
            if group == 'fans':
                field = self.fans
                person = user.student
            elif group == 'teachers':
                field = self.teachers
                person = user.employee
            elif group == 'helpers':
                field = self.helpers
                person = user.employee
            field.remove(person)
            self.save()
        except Student.DoesNotExist:
            raise NonStudentException()
        except Employee.DoesNotExist:
            raise NonEmployeeException()            
                
    def fans_count(self):
        """
            Count fans
        """
        return self.fans.all().count()
        
    def teachers_count(self):
        """
            Count teachers
        """
        return self.teachers.all().count()
        
    def helpers_count(self):
        """
            Count helpers
        """
        return self.helpers.all().count()
    
    def __unicode__(self):
        return self.name

    def in_offer(self):
        """
            Checks if course is in offer
        """
        return self.status > 0
    
    def in_summer( self ):
        """
            Checks if course is in summer semester
        """
        return self.semester == 's'
        
    def in_winter( self ):
        """
            Checks if course is in winter semester
        """
        return self.semester == 'w'

    @staticmethod
    def get_offer():
        return Proposal.filtred.filter(status__gt=0)

    @staticmethod
    def get_vote():
        return Proposal.filtred.filter(status=2)

    @staticmethod
    def get_winter():
        return Proposal.filtred.filter(semester='w')

    @staticmethod
    def get_summer():
        return Proposal.filtred.filter(semester='s')

    @staticmethod
    def get_unknown():
        return Proposal.filtred.filter(semester='u')
