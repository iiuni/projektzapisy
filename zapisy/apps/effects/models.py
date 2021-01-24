from django.db import models

from apps.users.models import Student
from apps.enrollment.courses.models.course_instance import CourseInstance


# Model for completed courses
class CompletedCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)# to_field='usos_kod') - usos_kod w CourseInstance nie jest 'unique'
    
    class Meta:
        unique_together = ('student', 'course')
    
    def get_completed_effects(student: Student):
        completed_courses = CompletedCourses.objects.filter(
            student=student.pk
        )

        done_effects = set() 
        for course in completed_courses:
            course_instance = CourseInstance.objects.get(id = course.course.id)
            for effect in course_instance.effects.all():
                done_effects.add(effect.group_name)

        return done_effects