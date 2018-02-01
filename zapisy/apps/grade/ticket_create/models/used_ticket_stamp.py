# -*- coding: utf-8 -*-
from django.db                import models
from apps.users.models      import Student

class UsedTicketStamp( models.Model ):
    from apps.grade.poll.models.poll import Poll
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name = "student" )
    poll    = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name = "ankieta" )
    class Meta:
        verbose_name        = 'wykorzystany bilet'
        verbose_name_plural = 'wykorzystane bilety'
        app_label           = 'ticket_create'
        
    def __unicode__(self):
        return unicode( self.student ) + " " + unicode( self.poll )
        
    @staticmethod
    def check_exists( student, poll ):
        return len( UsedTicketStamp.objects.filter( student = student, poll = poll )) == 0

    @staticmethod
    def get_grading_students_ids():
        return UsedTicketStamp.objects.all().values_list( 'student', flat = True ).distinct()
