from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.utils.decorators import method_decorator

from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import RecordStatus
from apps.enrollment.utils import mailto
from apps.enrollment.courses import utils


class CoursesListView(View):
    """Displays a basic courses view."""

    def get(self, request, semester_id: Optional[int] = None):
        if semester_id is None:
            semester = Semester.get_upcoming_semester()
        else:
            semester = get_object_or_404(Semester, pk=semester_id)
        data = utils.prepare_courses_list_data(semester)
        return render(request, 'courses/courses.html', data)


class CourseDetailView(View):
    """Displays the course detail view.

    It uses the shared logic in `course_view_data` from the utils module.
    """

    def get(self, request, slug: str):
        course, data = utils.course_view_data(request, slug)
        if course is None:
            raise Http404("Course not found")
        data.update(utils.prepare_courses_list_data(course.semester))
        return render(request, 'courses/courses.html', data)


@method_decorator(login_required, name='dispatch')
class CourseStudentListView(View):
    """Displays the student list for a course."""

    def get(self, request, course_slug: str, class_type: Optional[int] = None):
        course, _, groups_ids = utils.get_all_group_ids_for_course_slug(course_slug, class_type=class_type)
        if course is None:
            raise Http404("Course not found.")

        groups_data_enrolled = utils.get_group_data(groups_ids, request.user, status=RecordStatus.ENROLLED)
        groups_data_queued = utils.get_group_data(groups_ids, request.user, status=RecordStatus.QUEUED)
        students_in_course, students_in_queue = utils.get_students_from_data(groups_data_enrolled, groups_data_queued)
        can_user_see_all_students_here = any(
            group["can_user_see_all_students_here"]
            for group in groups_data_enrolled.values()
        ) or any(
            group["can_user_see_all_students_here"]
            for group in groups_data_queued.values()
        )

        data = {
            'students_in_course': students_in_course,
            'students_in_queue': students_in_queue,
            'course': course,
            'can_user_see_all_students_here': can_user_see_all_students_here,
            'mailto_group': mailto(request.user, students_in_course, bcc=False),
            'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
            'mailto_group_bcc': mailto(request.user, students_in_course, bcc=True),
            'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
            'class_type': class_type,
        }
        data.update(utils.prepare_courses_list_data(course.semester))
        return render(request, 'courses/course_list.html', data)
