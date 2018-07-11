from django.core.management.base import BaseCommand
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.grade.ticket_create.models.used_ticket_stamp import UsedTicketStamp


class Command(BaseCommand):
    args = '<semester( szablon)+>'
    help = 'tworzy ankiety na podstawie szablony'

    def handle(self, *args, **options):
        for p in UsedTicketStamp.objects.select_related('student', 'poll', 'poll__semester').all():
            st, c = StudentGraded.objects.get_or_create(student=p.student, semester=p.poll.semester)
