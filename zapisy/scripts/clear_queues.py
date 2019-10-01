from apps.enrollment.courses.models import Group
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.courses.models.group import GuaranteedSpots
from django.contrib.auth.models import Group as AuthGroup


def run():
    turns = ['tura1', 'tura2', 'tura3']
    course_slugs = [
        'analiza-matematyczna-201920-zimowy', 'kurs-podstawowy-warsztat-informatyka-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-c-201920-zimowy',
        'kurs-wstep-do-programowania-w-jezyku-python-201920-zimowy',
        'wstep-do-informatyki-201920-zimowy'
    ]
    course_groups = Group.objects.filter(course__slug__in=course_slugs)
    roles = AuthGroup.objects.filter(name__in=turns)
    Record.objects.filter(group__in=course_groups, status=RecordStatus.QUEUED).delete()
    for gr in course_groups:
        limit = gr.limit
        for gs in GuaranteedSpots.objects.filter(group=gr, role__in=roles):
            limit = limit + gs.limit
        GuaranteedSpots.objects.filter(group=gr, role__in=roles).delete()
        gr.limit = limit
        gr.save()
