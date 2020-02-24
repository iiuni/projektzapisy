from django.core.management.base import BaseCommand

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll

HEADER = "-- "
MARGIN = "   "
CREATED = " + "


class Command(BaseCommand):
    help = "Creates polls for a given semester. If not specified, current is assumed."

    def add_arguments(self, parser):
        parser.add_argument("-s", "--semester", type=str, help="ID of the semester")

    def handle(self, *args, **kwargs):
        semester_id = kwargs["semester"]
        created, skipped = 0, 0

        if semester_id:
            semester = Semester.objects.get(id=semester_id)
        else:
            semester = Semester.get_current_semester()

        self.stdout.write(f"Selected semester: `{semester}` with id {semester.id}")

        # Check whether poll exists for a selected semester
        self.stdout.write(f"\n{HEADER}Semester polls")
        semester_poll = Poll.objects.filter(semester=semester).count() > 0
        if semester_poll:
            self.stdout.write(f"{MARGIN}Poll for a selected semester already exists")
            skipped += 1
        else:
            new_poll = Poll(group=None, course=None, semester=semester)
            new_poll.save()
            self.stdout.write(
                f"{CREATED}Poll for a selected semester does not exist, creating"
            )
            created += 1

        # Check whether poll exists for courses held in a selected semester
        self.stdout.write(f"\n{HEADER}Course/group polls")
        courses = CourseInstance.objects.filter(semester=semester)

        for course in courses:
            course_poll = Poll.objects.filter(course=course).count() > 0
            if not course.has_exam or course_poll:
                self.stdout.write(f"{MARGIN}{course}")
                skipped += 1
            else:
                new_poll = Poll(group=None, course=course, semester=None)
                new_poll.save()
                self.stdout.write(f"{CREATED}{course}")
                created += 1

            groups = Group.objects.filter(course=course)

            for group in groups:
                group_poll = Poll.objects.filter(group=group).count() > 0
                if group_poll:
                    self.stdout.write(f"{MARGIN}{MARGIN}{group}")
                    skipped += 1
                else:
                    new_poll = Poll(group=group, course=None, semester=None)
                    new_poll.save()
                    self.stdout.write(f"{CREATED}{MARGIN}{group}")
                    created += 1

        self.stdout.write(f"\n{HEADER}Summary")
        self.stdout.write(f"{MARGIN}Created: {created}, skipped: {skipped}")
