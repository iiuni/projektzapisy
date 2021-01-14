from django.shortcuts import render

from apps.users.models import Student
from apps.enrollment.effects.models import Effect
from apps.enrollment.courses.models import CourseInstance
from apps.effects.models import CompletedCourses 

# Create your views here.
@login_required
def effects(request):
    
    student: Student = request.user.student

    completed_courses = CompletedCourses.objects.filter(
        student=student.pk
    )

    done_effects = set() 
    for course_id in completed_courses:
        course = CourseInstance.objects.get(id = course_id)
        for effect in course.effects:
            done_effects.add(course.group_name)

    data = {
        'effects' : done_effects
    }

    return render(request, 'effects/effects.html', data)
