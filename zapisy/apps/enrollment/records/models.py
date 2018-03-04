#-*- coding: utf-8 -*-
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from apps.enrollment.records.exceptions import NonGroupException
from apps.enrollment.records.exceptions import ECTS_Limit_Exception 
from apps.enrollment.records.exceptions import InactiveStudentException

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group  import Group
from apps.enrollment.courses.models.semester import Semester

from django.contrib.auth.models import User
from django.db import models

from apps.users.models import Student

from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.exceptions import NonCourseException

from datetime import datetime, timedelta, date
from itertools import cycle

from django.db.models import signals
from apps.enrollment.utils import mail_enrollment_from_queue
import logging
logger = logging.getLogger('project.default')
backup_logger = logging.getLogger('project.backup')

class EnrolledManager(models.Manager):
    def get_queryset(self):
        """ Returns only enrolled students. """
        # hate to do it like this but seems like there is no other way
        return super(EnrolledManager, self).get_queryset().filter(status='1')

class PinnedManager(models.Manager):
    def get_queryset(self):
        """ Returns only enrolled students. """
        # hate to do it like this but seems like there is no other way
        return super(PinnedManager, self).get_queryset().filter(status='2')

class Record(models.Model):

    STATUS_REMOVED = '0'
    STATUS_ENROLLED = '1'
    STATUS_PINNED = '2'

    RECORD_STATUS = [(STATUS_REMOVED, u'usunięty'), (STATUS_ENROLLED, u'zapisany'), (STATUS_PINNED, u'przypięty')]

    group = models.ForeignKey(Group, verbose_name='grupa', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name='student', related_name='records', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=RECORD_STATUS, verbose_name='status')

    created = models.DateTimeField(auto_now_add=True, verbose_name='utworzono')
    edited  = models.DateTimeField(auto_now=True, verbose_name='zmieniano')
    
    objects = models.Manager()
    enrolled = EnrolledManager()
    pinned = PinnedManager()

#    def delete(self, using=None):
#        self.status = STATUS_REMOVED
#        old = Record.objects.get(id=self.id)
#        if old.status <> STATUS_REMOVED:
#            self.group.remove_from_enrolled_counter(self.student)
#        self.save()

    def get_semester_name(self):
        return self.group.course.semester.get_name()

    def student_remove(self, student):
        self.group.remove_from_enrolled_counter(student)

        self.group.save()
        self.status=self.STATUS_REMOVED
        self.save()

    @staticmethod
    def get_student_records_for_course(student, course):
        return Record.objects.filter(student=student, status=Record.STATUS_ENROLLED, group__course=course).select_related('group')

    @staticmethod
    def get_student_records_for_group_type(student, group):
        return Record.get_student_records_for_course(student, group.course).filter(group__type=group.type)

    @staticmethod
    def recorded_students(students):
        """ Returns students with information about his/her records """
        
        recorded = Record.enrolled.distinct().\
                   values_list('student__user__id', flat=True).\
                   order_by('student__user__id')
        
        for student in students: # O(n^2) - da sie liniowo, jezeli posortujemy po id a nie nazwiskach
            student.recorded = student.id in recorded
        
        return students

    @staticmethod
    def get_student_records_ids(student, semester):
        records = Record.objects.\
            filter(student=student, group__course__semester=semester, status__gte=1).\
            values_list('group__pk', 'status')
        pinned = []
        enrolled = []
        for record in records:
            if int(record[1]) == 1:
                enrolled.append(record[0])
            else:
                pinned.append(record[0])
        return {
            'enrolled': enrolled,
            'pinned': pinned,
            'queued': Queue.queued.filter(student=student,
                      group__course__semester=semester, deleted=False).\
                      values_list('group__pk', flat=True)
        }
    
    @staticmethod
    def get_student_enrolled_objects(student, semester):
        '''
            TODO: po wywaleniu get_student_records zmienić nazwę na właśnie tą
        '''
        return Record.enrolled.\
            filter(student=student, group__course__semester=semester).\
            select_related('group', 'group__course', 'group__course__entity',\
            'group__course__entity__type')
    
    @staticmethod
    def get_student_enrolled_ids(student, semester):
        return Record.enrolled.\
            filter(student=student, group__course__semester=semester).\
            values_list('group__pk', flat=True)
    
    @staticmethod
    def get_student_records(student):
        '''
            TODO: DEPRECATED
        '''
        records = Record.enrolled.filter(student=student).\
            select_related('group', 'group__course', 'group__teacher',
                'group__teacher__user', 'group__term').\
                order_by('group__course__entity__name')
        groups = [record.group for record in records]
        for group in groups:
            group.terms_ = group.get_all_terms() # za dużo zapytań
            group.course_ = group.course
        return groups
    
    @staticmethod
    def get_groups_with_records_for_course(slug, user_id, group_type):
        user = User.objects.get(id=user_id)
        try:
            course = Course.objects.get(slug=slug)
            groups = Group.objects.filter(course=course).filter(type=group_type)
            try:
                student_groups = Record.get_groups_for_student(user)
            except NonStudentException:
                logger.warning('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
                student_groups = {}
            for g in groups:
                g.priority = Queue.get_priority(user_id, g.id)
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = g.get_count_of_enrolled()
                g.queued = g.get_count_of_queued()
                g.is_in_diff = Record.is_student_in_course_group_type(user=user, slug=slug, group_type=group_type)
                if g in student_groups:
                    g.signed = True
                if g.enrolled < g.limit:
                    g.is_full = False
                else:
                    g.is_full = True
        except Course.DoesNotExist:
            logger.warning('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonCourseException()
        return groups
    
    @staticmethod
    def get_students_in_group(group_id):
        try:
            return Student.objects.filter(records__group_id=group_id, records__status=1).select_related('program', 'user', 'zamawiane', 'zamawiane2012')
        except Group.DoesNotExist:
            raise NonGroupException()
    
    @staticmethod
    def get_groups_for_student(user):
        try:
            student = user.student
            return map(lambda x: x.group, \
                Record.enrolled.filter(student=student).\
                select_related('group', 'group__course'))
        except Student.DoesNotExist:
            logger.warning('Record.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user.id))
            raise NonStudentException()
    
    @staticmethod
    def is_student_in_course_group_type(user, slug, group_type):
        try:
            course = Course.objects.get(slug=slug)
            user_course_group_type = [g.id for g in Record.get_groups_for_student(user) if g.course == course and g.type == group_type]
            if user_course_group_type:
                return user_course_group_type[0]
            return False
        except Student.DoesNotExist:
            logger.warning('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user.id), unicode(group_type)))
            raise NonStudentException()
        except Course.DoesNotExist:
            logger.warning('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Course.DoesNotExist exception.' % (unicode(slug), int(user.id), unicode(group_type)))
            raise NonCourseException()
    
    @staticmethod
    def pin_student_to_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record, is_created = Record.objects.get_or_create(group=group, student=student, status=Record.STATUS_PINNED)
            if is_created == False:
                logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) raised AlreadyPinnedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyPinnedException()
            logger.info('User %s <id: %s> is now pinned to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
            return record
        except Student.DoesNotExist:
            logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Student.DoesNotExists exception.' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Group.DoesNotExists exception.' % (int(user_id), int(group_id)))
            raise NonGroupException()
    
    @staticmethod
    def unpin_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.objects.get(group=group, student=student, status=Record.STATUS_PINNED)
            record.delete()
            logger.info('User %s <id: %s> is no longer pinned to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
            return record
        except Record.DoesNotExist:
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Record.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise AlreadyNotPinnedException()
        except Student.DoesNotExist:
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Student.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Group.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonGroupException()
    
    @staticmethod
    def add_student_to_lecture_group(user, course):
        """ assignes student to lectures group for a given course """
        try:
            student = user.student
            lectures = Group.objects.filter(course=course, type__in=['1','9'])
            groups = Record.get_groups_for_student(user)
            new_records = []
            for l in lectures:
                #TODO: nie podoba mi się to
                if (l not in groups) and (l.get_count_of_enrolled(dont_use_cache=False) < l.limit):
                    record, created = Record.objects.get_or_create(group=l, student=student)
                    if created:
                        record.status = Record.STATUS_ENROLLED
                        record.save()
                    elif record.status == Record.STATUS_PINNED:
                            record.status = Record.STATUS_ENROLLED
                            record.save()
                    new_records.append(record)
                    try:
                        queued = Queue.queued.get(group=l, student=student)
                        queued.delete()
                    except Queue.DoesNotExist:
                        pass
                    logger.info('User %s <id: %s> is automaticaly added to lecture <id: %s> of Course: [%s] <id: %s>' % (user.username, user.id, l.id, course.name, course.id))
                    backup_logger.info('[02] user <%s> is automaticaly added to lecture group <%s>' % (user.id, l.id))
            return new_records
        except Student.DoesNotExist:
            logger.warning('Record.add_student_to_lecture_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, course_id = %d)' % (int(user.id), int(course.id)))
            raise NonStudentException()


    def group_slug(self):
        return self.group.course_slug()
    
    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
    
    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.course, self.group.get_type_display(), self.group.get_teacher_full_name())

class QueueManager(models.Manager):
    def get_queryset(self):
        """ Returns only queued students. """
        return super(QueueManager, self).get_queryset()
    

def queue_priority(value):
    """ Controls range of priority"""
    if value <= 0 or value > 10:
        raise ValidationError(u'%s is not a priority' % value)

class Queue(models.Model):
    group   = models.ForeignKey(Group, verbose_name='grupa', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name='student', related_name='queues', on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='Czas dołączenia do kolejki', auto_now_add=True)
    edited = models.DateTimeField(verbose_name='Czas ostatniej zmiany', auto_now=True)
    priority = models.PositiveSmallIntegerField(default=1, validators=[queue_priority], verbose_name='priorytet')

    deleted = models.BooleanField(default=False)

    objects = models.Manager()
    queued = QueueManager()

#    def delete(self, using=None):
#        self.deleted = True
#        old = Queue.objects.get(id=self.id)
#        if not old.deleted:
#            self.group.remove_from_queued_counter(self.student)
#        self.save()


    def set_priority(self, value):
        self.priority = value
        self.save()
        return self

    @staticmethod
    def get_student_queues(student, semester):
        return Queue.queued.filter(student=student,
            group__course__semester=semester, deleted=False)
#        for queue in raw:
#            queues[queue.id] = queue
#        return queues

    @staticmethod
    def get_priority(user_id, group_id):
        """ Returns priority of student in group queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id = group_id)
            """Pobranie recordu z zapisem studenta do kolejki grupy"""
            queue = Queue.queued.filter(student=student, group=group, deleted=False)
            if queue:
                return queue[0].priority
            else:
                return False
        except Student.DoesNotExist:
            logger.warning('Queue.get_priority() throws Student.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.get_priority() throws Group.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonGroupException()
            
    
    @staticmethod
    def get_students_in_queue(group_id):
        """ Returns state of queue for group ordered by time (FIFO)."""
        try:
            qq = Queue.objects.filter(deleted=False, group_id=group_id).select_related('student', 'student__user').order_by('time')
            p = []
            for q in qq:
                p.append(q.student)
            return p

        except Group.DoesNotExist:
            logger.warning('Queue.get_students_in_queue() throws Group.DoesNotExist(parameters : group_id = %d)' % int(group_id))
            raise NonGroupException()
    
    @staticmethod
    def change_student_priority(user_id, group_id, new_priority) :
        """change student's priority in group queue"""
        try:
            student = Student.objects.select_related('user').get(user__id=user_id)
            record = Queue.objects.select_related('group').get(student=student, group__id=group_id)
            """ Podstawienie nowej wartości"""
            record.priority = new_priority
            record.save()
            logger.info('User %s <id: %s> changed queue priority of group "%s" <id: %s> to %s' % (student.user.username, student.user.id, record.group, record.group.id, new_priority))
            return record
        except Queue.DoesNotExist:
            logger.warning('Queue.change_student_priority() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonGroupException()
    
    @staticmethod
    def remove_student_from_queue(user_id, group_id):
        """remove student from queue"""
        try:
            student = Student.objects.select_related('user').get(user__id=user_id)

            record = Queue.queued.select_related('group').get(
                group__id=group_id, student=student, deleted=False)
            group = record.group
            record.delete()
            logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s>' % (student.user.username, student.user.id, group, group.id))
            return record
        except Queue.DoesNotExist:
            logger.warning('Queue.remove_student_from_queue() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.warning('Queue.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()
    

    @staticmethod
    def get_groups_for_student(user):
        """ Return all groups that student is trying to sign to."""
        try:
            student = user.student
            return map(lambda x: x.group, Queue.queued.filter(student=student))
        except Student.DoesNotExist:
            logger.warning('Queue.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user.id))
            raise NonStudentException()
    
    @staticmethod
    def remove_student_low_priority_records(user_id, group_id, priority) :
        """ Funkcja, która czyści kolejkę z wpisów do grup z tego samego przedmiotu o tym samym rodzaju ale mniejszym priorytecie"""
        user = User.objects.get(id = user_id)
        try:

            """ Pobranie listy grup z tego samego przedmiotu i tego samego typu, na które próbuje się zapisać student"""
            """ Dalej są jakieś herezje, imho powinno być:
            group = Group.objects.get(id = group_id).select_related('course')
            queued = Queue.queued.filter(student=user.student, group__course=group.course, group__type=group.type).select_related('group') #jedno zapytanie zamiast kilkudziesieciu!!!!
                for queue in queued:
                    if queue.priority <= priority:
                        logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s> because of low priority (%s)' % (user.username, user.id, queue.group, queue.group.id, priority))
                        Queue.remove_student_from_queue(user_id,q_g.id)
            """
            student = user.student
            group = Group.objects.get(id = group_id)
            course = Course.objects.get(slug = group.course_slug())
            queued_group = [g for g in Queue.get_groups_for_student(user) if g.course == course and g.type == group.type]
            """ Usunięcie wszystkich wpisów z kolejki, które są na liście queued_group i posiadają niższy priorytet od zadanego"""
            for q_g in queued_group :
                record = Queue.queued.get(student = student,group = q_g) #WTF?!
                if (record.priority <= priority) :
                    logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s> because of low priority (%s)' % (user.username, user.id, q_g, q_g.id, priority))
                    Queue.remove_student_from_queue(user_id,q_g.id)
        except Student.DoesNotExist:
            logger.warning('Queue.remove_student_low_priority_records throws Student.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.remove_student_low_priority_records throws Group.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonGroupException()

    @staticmethod
    def queue_priorities_map(queue_set):
        raw = queue_set.values('group__id', 'priority')
        m = {}
        for r in raw:
            m[r['group__id']] = r['priority']
        return m
    
    @staticmethod
    def queue_priorities_map_values(queue_values):
        m = {}
        for r in queue_values:
            m[r['group_id']] = r['priority']
        return m

    def group_slug(self):
        return self.group.course_slug()
    
    class Meta:
        verbose_name = 'kolejka'
        verbose_name_plural = 'kolejki'
    
    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.course, self.group.get_type_display(), self.group.get_teacher_full_name())

def log_add_record(sender, instance, created, **kwargs):
    if instance.status == Record.STATUS_ENROLLED:
        backup_logger.info('[01] user <%s> is added to group <%s>' % (instance.student.user.id, instance.group.id))
        
def log_delete_record(sender, instance, **kwargs):
    if instance.status == Record.STATUS_ENROLLED and instance.group:
        backup_logger.info('[03] user <%s> is removed from group <%s>' % (instance.student.user.id, instance.group.id))


#signals.post_save.connect(log_add_record, sender=Record)
#signals.pre_delete.connect(log_delete_record, sender=Record)
#signals.post_delete.connect(Record.on_student_remove_from_group, sender=Record)
#signals.post_save.connect(add_people_from_queue, sender=Group)
