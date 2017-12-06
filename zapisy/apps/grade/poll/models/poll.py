# -*- coding: utf-8 -*-
from django.db                         import models
from django.utils.safestring           import SafeUnicode

from apps.users.models               import Employee, \
                                              Student, \
                                              Program
from apps.enrollment.courses.models.group import Group, \
                                              GROUP_TYPE_CHOICES

from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.course import Course

from apps.enrollment.records.models  import Record
from .section                           import SectionOrdering
from .saved_ticket                       import SavedTicket
from .origin                          import Origin

class Poll( models.Model ):

    author            = models.ForeignKey( Employee, verbose_name = 'autor', related_name = 'author' )
    title             = models.CharField( max_length = 40, verbose_name = 'tytuł' )
    description       = models.TextField( blank = True, verbose_name = 'opis' )
    semester          = models.ForeignKey( Semester, verbose_name = 'semestr' )
    group             = models.ForeignKey( Group, verbose_name = 'grupa', blank = True, null = True )
    studies_type      = models.ForeignKey( Program, verbose_name = 'typ studiów', blank = True, null = True )
    share_result      = models.BooleanField( verbose_name = 'udostępnij wyniki', default = False, blank = True )

    finished          = models.BooleanField( verbose_name="zakończona", default=False)

    deleted           = models.BooleanField( blank = False, null = False, default = False, verbose_name = 'usunięta' )
    origin            = models.ForeignKey( Origin, verbose_name='zbiór', default=None, blank = True, null= True)

    class Meta:
        verbose_name        = 'ankieta' 
        verbose_name_plural = 'ankiety'
        app_label           = 'poll'
        
    def __unicode__( self ):
        res = str( self.title )
        if self.group: res += ', ' + str(self.group.get_type_display()) + " - " + str(self.group.get_teacher_full_name())
        if self.studies_type: res += ', typ studiów: ' + str( self.studies_type )
        return res
        
    def to_url_title( self, break_lines = False ):
        res = str( self.title )
        if break_lines:
            sep = '<br>'
        else:
            sep = ', '
            
        if self.group:
            res += ': '   + self.group.get_teacher_full_name()
        else:
            res += sep + 'Ankieta ogólna'
            
        if self.studies_type: 
            res += sep + 'typ studiów: ' + str( self.studies_type )
        
        return SafeUnicode( res )
        
    def is_student_entitled_to_poll( self, student ):
        if self.group:
            rec = Record.objects.filter( student = student, 
                                         group   = self.group,
                                         status  = Record.STATUS_ENROLLED )
            try:                
                rec[ 0 ]
            except:
                return False
                
        if self.studies_type:
            if self.studies_type != student.program:
                return False
        
        return True 
    
    def is_user_entitled_to_view_result( self, user ):
        if not user.is_authenticated(): return False
        if user.is_superuser: return True
        if self.share_result: return True
        
        try:
            viewer  = user.employee
            
            if self.group:
                if viewer == self.group.teacher: return True
                
                lecture = filter( lambda x_y: x_y[1] == 'wykład', GROUP_TYPE_CHOICES )[ 0 ][ 0 ]
                groups  = Group.objects.filter( course = self.group.course,
                                                teacher = viewer,
                                                type    = lecture )
                if groups: return True
            else:
                # Zakładam, że wszyscy pracownicy powinni widzieć wyniki ankiet
                # ogólnych
                return True
        except Employee.DoesNotExist: 
            pass
        
        return False
               
    def all_sections( self ):
        return self.section_set.all()
    
    def all_answers( self ):
        result = []
        for section in self.all_sections():
            result.append( section.all_answers( self ))
        return result
    
    def as_row( self ):
        from apps.grade.ticket_create.models.public_key import PublicKey

        res  = "<tr><td>"
        res += str( self.pk ) + '</td><td>'
        res += str( self.title ) + '</td><td>'
        
        if self.group:
            res += str( self.group.course.name ) + '</td><td>'
            res += str( self.group.get_type_display()) + '</td><td>'
            res += str( self.group.get_teacher_full_name()) + '</td><td>'
        else:
            res += '-</td><td>-</td><td>-</td><td>'
        
        if self.studies_type:
            res += str( self.studies_type ) + '</td><td>'
        else:
            res += '-</td><td>'
            
        res += str( " &#10;".join(PublicKey.objects.get( poll = self.pk ).public_key.split('\n')))
        res += '</td></tr>'
        return SafeUnicode( res )
    
    @staticmethod
    def get_polls_for_semester( semester = None):
        if not semester:
            semester = Semester.get_current_semester()
        return Poll.objects.filter( semester = semester, deleted = False ).select_related('group', 'group__course', 'group__teacher', 'group__teacher__user')
    
    @staticmethod
    def get_groups_without_poll():
        semester = Semester.get_current_semester()
        polls    = Poll.objects.filter( semester = semester, group__isnull=False, deleted = False ).order_by('pk') 
        polls    = [p.group_id for p in polls]
        groups   = Group.objects.filter(course__semester = semester).order_by('pk')
        return [g for g in groups if g.pk not in polls]
    
    @staticmethod
    def get_current_polls(student=None):
        semester = Semester.objects.get(is_grade_active=True)
        where = ['((SELECT COUNT(*) FROM ticket_create_publickey WHERE poll_id = poll_poll.id GROUP BY poll_id) > 0)']
        if student:
            count = '((SELECT COUNT(*) FROM ticket_create_usedticketstamp WHERE poll_id = poll_poll.id AND student_id = %d) = 0)' % student.id
            where.append( count )

        return Poll.objects.filter(deleted=False, semester=semester  )\
                    .select_related('semester', 'studies_type')\
                    .extra(where=where)


    @staticmethod
    def get_semester_polls_without_keys(semester = None):
        from apps.grade.ticket_create.models.public_key import PublicKey
        if not semester:
            semester = Semester.get_current_semester()

        polls_with_keys = PublicKey.objects.all().values_list( 'poll' )
        return Poll.objects.filter( semester = semester, deleted=False ).exclude( pk__in = polls_with_keys)

    @staticmethod
    def get_polls_without_keys(semester=None):
        from apps.grade.ticket_create.models.public_key import PublicKey

        polls_with_keys = PublicKey.objects.filter(poll__semester=Semester)
        return Poll.objects.filter( semester=semester, deleted=False ).exclude( pk__in = polls_with_keys)

    @staticmethod
    def get_current_semester_polls_without_keys():
        return Poll.get_semester_polls_without_keys()

    @staticmethod
    def count_polls_without_keys():
        from apps.grade.ticket_create.models.public_key import PublicKey

        polls_with_keys = PublicKey.objects.all()
        return Poll.objects.filter(deleted=False ).exclude( pk__in = polls_with_keys).count()

    @staticmethod
    def count_current_semester_polls_without_keys():
        from apps.grade.ticket_create.models.public_key import PublicKey

        semester = Semester.get_current_semester()
        polls_with_keys = PublicKey.objects.all().values( 'poll' )
        return Poll.objects.filter( semester = semester, deleted=False ).exclude( pk__in = polls_with_keys).count()

    @staticmethod
    def get_polls_list( student ):
        polls = Poll.get_all_polls_for_student(student)
        courses = {}
        general = []
        for poll in polls:

            if poll.group:

                if not poll.group.course_id in courses:
                    courses[poll.group.course_id] = { 'courses': poll.group.course, 'polls': [] }
                courses[poll.group.course_id]['polls'].append(poll)
            else:
                general.append(poll)

        return courses, general


    @staticmethod
    def get_all_polls_for_student( student ):
        groups = Record.objects.filter( student = student,
                                                 status  = Record.STATUS_ENROLLED ).select_related('group')\
                                .values_list('group__id', flat=True)

        return [x for x in Poll.get_current_polls(student=student) if not x.group or x.group.id in groups]
    
    @staticmethod
    def get_all_polls_for_group( group, semester = None ):
        if not semester:
            semester = Semester.get_current_semester()
        return Poll.objects.filter( semester = semester, group = group, deleted=False )
    
    def get_section_by_id(self, section_id):
        return self.section_set.get(section__pk = section_id)
            
    def all_answers_by_tickets( self ):
        results = []
        tickets = SavedTicket.objects.filter( poll = self, finished = True)
        sections = self.all_sections()
        for ticket in tickets:
            sections_answers = []
            # for each section, we want to get all the answers for this section's questions - and in the right order!
            for section in sections:
                answers_in_section = section.all_answers_for_ticket(self, ticket)
                sections_answers.append( answers_in_section )                
            #print sections_answers
            results.append( (ticket, sections_answers) ) 
        return results
