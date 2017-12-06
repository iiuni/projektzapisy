# -*- coding: utf-8 -*-
from django.test                       import TestCase
from .utils                             import generate_keys_for_polls, \
                                              group_polls_by_course
from .models                            import PublicKey, \
                                              PrivateKey
from apps.grade.poll.models          import Poll
from apps.users.models               import Employee, \
                                              Student
from apps.enrollment.courses.models import Semester
                        
class UtilsTest( TestCase ):
    
    fixtures = [ 'test_ticket_create.json' ]
    
    def setUp( self ):
        pass
    
    def test_generate_keys_for_polls_generates_keys_for_each_poll( self ):
        polls = Poll.objects.all()
        for poll in polls:
            self.assertEqual( list( poll.publickey_set.all()), [] )
            self.assertEqual( list( poll.privatekey_set.all()), [] ) 
        generate_keys_for_polls()
        for poll in polls:
            self.assertNotEqual( list( poll.publickey_set.all()), [] )
            self.assertNotEqual( list( poll.privatekey_set.all()), [] ) 
        
        
    def test_generate_keys_for_polls_generates_keys_for_new_polls_only( self ):
        polls = Poll.objects.all()
        generate_keys_for_polls()
        for poll in polls:
            self.assertEqual( len( list( poll.publickey_set.all())), 1 )
            self.assertEqual( len( list( poll.privatekey_set.all())), 1 ) 
            
        new_poll = Poll( author      = Employee.objects.get( pk = 1 ),
                         title       = "test",
                         description = "brak",
                         semester    = Semester.get_current_semester())
        new_poll.save()
        
        generate_keys_for_polls()
        
        self.assertEqual( len( list( new_poll.publickey_set.all())), 1 )
        self.assertEqual( len( list( new_poll.privatekey_set.all())), 1 ) 
        for poll in polls:
            self.assertEqual( len( list( poll.publickey_set.all())), 1 )
            self.assertEqual( len( list( poll.privatekey_set.all())), 1 )
        
    def test_generate_keys_for_polls_do_not_change_saved_keys( self ):
        polls = Poll.objects.all()
        generate_keys_for_polls()
        pre_keys = []
        for poll in polls:
            c_keys = []
            self.assertEqual( len( list( poll.publickey_set.all())), 1 )
            self.assertEqual( len( list( poll.privatekey_set.all())), 1 ) 
            c_keys.append( poll.publickey_set.all()[0] )
            c_keys.append( poll.privatekey_set.all()[0] )
            pre_keys.append( c_keys )
        
        generate_keys_for_polls()
        post_keys = []
        for poll in polls:
            c_keys = []
            self.assertEqual( len( list( poll.publickey_set.all())), 1 )
            self.assertEqual( len( list( poll.privatekey_set.all())), 1 ) 
            c_keys.append( poll.publickey_set.all()[0] )
            c_keys.append( poll.privatekey_set.all()[0] )
            post_keys.append( c_keys )
        
        self.assertEqual( pre_keys, post_keys )
        
    def test_group_polls_by_course_makes_valid_groups( self ):
        generate_keys_for_polls()
        polls = Poll.get_all_polls_for_student( Student.objects.get( pk = 1 ))
        groupped = group_polls_by_course( polls )
        
        for group in groupped:
            if group[0].group:
                course = group[0].group.course
            else:
                course = None
            for poll in group:
                if course:
                    self.assertEqual( course, poll.group.course )
                else:
                    self.assertEqual( course, poll.group )
        
