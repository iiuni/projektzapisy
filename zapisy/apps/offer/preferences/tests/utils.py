# -*- coding:utf-8 -*-

from django.test import TestCase

from apps.offer.proposal.models import Proposal
from apps.users.models import Employee

class GetEmployeesUnsetTest(TestCase):
    fixtures = ['three_employees.json', 
                'preferences_testing_data.json']
    
    def setUp(self):
        self.emp1 = Employee.objects.get(user__username='emp1')
        self.emp2 = Employee.objects.get(user__username='emp2')
        self.emp3 = Employee.objects.get(user__username='emp3')
        self.course1 = Proposal.objects.get(name='Kurs 1')
        self.course2 = Proposal.objects.get(name='Kurs 2')
        self.seminar = Proposal.objects.get(name='Seminarium 1')
    
    def test_get_employees_unset(self):
        self.assertEquals(
            set(get_employees_unset(self.emp1)),
            set([self.course1, self.course2, self.seminar]))
        self.assertEquals(
            set(get_employees_unset(self.emp2)),
            set([]))
        self.assertEquals(
            set(get_employees_unset(self.emp3)),
            set([self.course2, self.seminar]))
    
