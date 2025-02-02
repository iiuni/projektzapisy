from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.enrollment.records.models import RecordStatus
from apps.enrollment.utils import mailto
from apps.enrollment.courses.views import utils


@login_required
def group_view(request, group_id: int):
    """View for group records."""
    enrolled_data = utils.get_group_data([group_id], request.user, status=RecordStatus.ENROLLED)
    queued_data = utils.get_group_data([group_id], request.user, status=RecordStatus.QUEUED)
    students_in_group, students_in_queue = utils.get_students_from_data(
        enrolled_data, queued_data, preserve_queue_ordering=True
    )
    group = enrolled_data[group_id].get("group")
    data = {
        'students_in_group': students_in_group,
        'students_in_queue': students_in_queue,
        'guaranteed_spots': enrolled_data.get('guaranteed_spots_rules'),
        'group': group,
        'can_user_see_all_students_here': enrolled_data[group_id].get("can_user_see_all_students_here"),
        'mailto_group': mailto(request.user, students_in_group, bcc=False),
        'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
        'mailto_group_bcc': mailto(request.user, students_in_group, bcc=True),
        'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    }
    data.update(utils.prepare_courses_list_data(group.course.semester))
    return render(request, 'courses/group.html', data)
