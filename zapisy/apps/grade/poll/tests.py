# -*- coding: utf-8 -*-
from django.test                import TestCase
from django.contrib.auth.models import AnonymousUser, \
                                       User
from apps.users.models        import Student, \
                                       Employee
from apps.grade.poll.models   import Section, \
                                       SingleChoiceQuestion, \
                                       SingleChoiceQuestionOrdering, \
                                       MultipleChoiceQuestion, \
                                       OpenQuestion, \
                                       Poll

class Xd:
    x = "asdahgsdjgasjhdgjashgdjasgdashgdhasgdjhgsadgasgdahsgdhasgdshagdhasgdhgsadhgasdhgasdhgashgdashgdjasgdj"

class SectionTest( TestCase ):
    fixtures = [ 'section_test.json' ]
        
    def setUp( self ):
        self.section = Section.objects.get( pk = 1 )
            
    def test_all_questions_gets_only_current_section_questions( self ):
        for question in self.section.all_questions():
            self.assertEqual( self.section in question.sections.all(), True )
        
    def test_all_questions_gets_all_current_section_questions( self ):
        open_q     = list( self.section.openquestion_set.all())
        single_c_q = list( self.section.singlechoicequestion_set.all())
        multi_c_q  = list( self.section.multiplechoicequestion_set.all())
        
        for question in open_q + single_c_q + multi_c_q:
            self.assertEqual( question in self.section.all_questions(), True )
    
    def test_all_questions_is_leading_question_first( self ):
        lq_s  = self.section.all_questions()[ 0 ]
        lq_db = SingleChoiceQuestionOrdering.objects.get( sections = self.section,
                                                          is_leading = True ).question
        self.assertEqual( lq_s, lq_db )

    def test_questions_ordering( self ):
        for i, question in enumerate( self.section.all_questions()):
            self.assertEqual( unicode( question ).endswith( unicode( i + 1 )), True )

class PollTest( TestCase ):
    fixtures = [ 'poll_test.json' ]
    
    def setUp( self ):
        self.poll_group_only            = Poll.objects.get( pk = 1 )
        self.poll_group_and_s_type      = Poll.objects.get( pk = 2 )
        self.poll_global_s_type         = Poll.objects.get( pk = 3 )
        
        self.poll_global                = Poll.objects.get( pk = 4 )
        self.poll_lecture               = Poll.objects.get( pk = 1 )
        self.poll_exercisces_not_shared = Poll.objects.get( pk = 6 )
        self.poll_exercisces_shared     = Poll.objects.get( pk = 5 )
        
        self.valid_student              = Student.objects.get( pk = 1 )
        self.waiting_student            = Student.objects.get( pk = 4 )
        self.not_recorded_student       = Student.objects.get( pk = 2 )
        self.invalid_s_type_stud        = Student.objects.get( pk = 3 )
        
        self.anonymous                  = AnonymousUser()
        self.admin                      = User.objects.get( pk = 1 )
        self.student                    = Student.objects.get( pk = 1)
        self.lecturer                   = Employee.objects.get( pk = 1 )
        self.sharer                     = Employee.objects.get( pk = 2 )
        self.private                    = Employee.objects.get( pk = 3 )
        
    def test_student_recorded_to_group_is_entitled( self ):
        self.assertEqual( self.poll_group_only.is_student_entitled_to_poll( self.valid_student ), True )
        
    def test_waiting_student_is_not_entitled( self ):
        self.assertEqual( self.poll_group_only.is_student_entitled_to_poll( self.waiting_student ), False )

    def test_student_without_record_is_not_entitled( self ):
        self.assertEqual( self.poll_group_only.is_student_entitled_to_poll( self.not_recorded_student ), False )
    
    def test_student_with_valid_studies_type_and_valid_record_is_entitled( self ):
        self.assertEqual( self.poll_group_and_s_type.is_student_entitled_to_poll( self.valid_student ), True )
    
    def test_student_with_wrong_studies_type_and_valid_record_is_not_entitled( self ):
        self.assertEqual( self.poll_group_and_s_type.is_student_entitled_to_poll( self.invalid_s_type_stud ), False )
        
    def test_student_with_valid_studies_type_is_entitled_to_global_poll( self ):
        self.assertEqual( self.poll_global_s_type.is_student_entitled_to_poll( self.valid_student ), True )
    
    def test_student_with_wrong_studies_type_is_not_entitled_to_global_poll( self ):
        self.assertEqual( self.poll_global_s_type.is_student_entitled_to_poll( self.invalid_s_type_stud ), False )
        
    def test_no_requirements_every_student_entitled( self ):
        self.assertEqual( self.poll_global.is_student_entitled_to_poll( self.valid_student ), True )
        self.assertEqual( self.poll_global.is_student_entitled_to_poll( self.waiting_student ), True )
        self.assertEqual( self.poll_global.is_student_entitled_to_poll( self.not_recorded_student ), True )
        self.assertEqual( self.poll_global.is_student_entitled_to_poll( self.invalid_s_type_stud ), True )
    
    def test_admin_can_see_each_poll_result( self ):
        self.assertEqual( self.poll_global.is_user_entitled_to_view_result( self.admin ), True )
        self.assertEqual( self.poll_lecture.is_user_entitled_to_view_result( self.admin ), True )
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.admin ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.admin ), True )

    def test_employee_can_see_each_global_poll_result( self ):
        self.assertEqual( self.poll_global.is_user_entitled_to_view_result( self.lecturer.user ), True )
        self.assertEqual( self.poll_global.is_user_entitled_to_view_result( self.sharer.user ), True )
        self.assertEqual( self.poll_global.is_user_entitled_to_view_result( self.private.user ), True )
    
    def test_employee_can_see_his_result( self ):
        self.assertEqual( self.poll_lecture.is_user_entitled_to_view_result( self.lecturer.user ), True )
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.private.user ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.sharer.user ), True )
    
    def test_lecturer_can_see_all_results_from_his_course( self ):
        self.assertEqual( self.poll_lecture.is_user_entitled_to_view_result( self.lecturer.user ), True )
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.lecturer.user ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.lecturer.user ), True )
    
    def test_everyone_can_see_shared_result( self ):
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.lecturer.user ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.sharer.user ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.private.user ), True )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.student.user ), True )
        
    def test_no_one_can_see_private_result( self ):
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.sharer.user ), False )
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.student.user ), False )
        
    def test_non_authenticated_user_cannot_see_results( self ):
        self.assertEqual( self.poll_global.is_user_entitled_to_view_result( self.anonymous ), False )
        self.assertEqual( self.poll_lecture.is_user_entitled_to_view_result( self.anonymous ), False )
        self.assertEqual( self.poll_exercisces_not_shared.is_user_entitled_to_view_result( self.anonymous ), False )
        self.assertEqual( self.poll_exercisces_shared.is_user_entitled_to_view_result( self.anonymous ), False )
    
    # Nie ma testów pozostałych metod, bo byłyby to testy djangowych filtrów,
    # a tym ufamy, że działają
