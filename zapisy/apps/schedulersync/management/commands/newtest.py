from datetime import time
from datetime import date
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import environ
import requests

from django.contrib.auth.models import User, UserManager
from apps.users.models import Employee
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.models.group import Group
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.schedulersync.models import TermSyncData
from apps.schedulersync.models import EmployeeMap

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager




def create_map_employee(scheduler_id, sz_id):
    EmployeeMap.objects.create(scheduler_username=scheduler_id)


def getNN():
    cos = Employee.objects.get(user__username="Nn")
    print(cos)


def fun():
    prop = Proposal.objects.get(
        name__iexact='Kurs modelowania 3D i wizualizacji w programie SketchUp', status__in=[ProposalStatus.IN_OFFER,
                                                                                            ProposalStatus.IN_VOTE])
    sem = Semester.objects.get(year="2018/19", type='l')
    course = CourseInstance.objects.get(semester=sem, offer=prop)
    groups = Group.objects.filter(course=course, type='3', limit='15')

    for group in groups:
        print(group)
        print(group.course)
        print(group.teacher)
        print(group.get_terms_as_string())


def fun2():
    prop = Proposal.objects.get(
        name__iexact='Algorytmy i struktury danych (M)', status__in=[ProposalStatus.IN_OFFER,
                                                                     ProposalStatus.IN_VOTE])
    sem = Semester.objects.get(year="2018/19", type='l')
    course = CourseInstance.objects.get(semester=sem, offer=prop)
    groups = Group.objects.filter(course=course, type='3')

    sync_data_object = TermSyncData.objects.select_related(
        'term', 'term__group').prefetch_related('term__classrooms').get(
        scheduler_id=groups[0].scheduler_id, term__group__course__semester=sem)

    term = sync_data_object.term

    print("term classromms = ", term.classrooms)

    for group in groups:
        print(group)
        print(group.limit)
        print(group.course)
        print(group.teacher)
        print(group.get_terms_as_string())


def fun3():
    sem = Semester.objects.get(year="2018/19", type='l')
    gr = Group.objects.filter(course__semester=sem, type='1')[8]
    print(gr)
    for attr in vars(gr):
        print("%s = %r" % (attr, getattr(gr, attr)))
    tr = Term.objects.get(group=gr)
    print("\n", tr)
    for attr in vars(tr):
        print("%s = %r" % (attr, getattr(tr, attr)))


def fun4():
    sem = Semester.objects.get(year="2018/19", type='l')
    sync_data_objects = TermSyncData.objects.all()
    for x in range(200):
        print(sync_data_objects[x].term.classrooms)

def fun5():
    emp = Employee.objects.get(user__username='cahir')
    print(emp)
    print(emp.id)
    user = User.objects.get(username='cahir')
    full_name = user.get_full_name()
    print(full_name)


#   print("grupa =", sync_data_objects.term.group)
#  print("term =", sync_data_objects.term)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true')


    def handle(self, *args, **options):
        print(os.environ['CD'])
