from django.core.management.base import BaseCommand, CommandError
from apps.grade.ticket_create.models import StudentGraded
from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student


class Command(BaseCommand):
    args = '<plik semester>'
    help = 'ocenia'

    def handle(self, *args, **options):
        print "Plik: " + args[0]
        f = open(args[0], 'r+')
        for line in f:
            print line
            u = StudentGraded()
            try:
                u.student = Student.objects.get(matricula=line.rstrip())
                u.semester_id = args[1]
                u.save()
                print "ok"
            except ObjectDoesNotExist:
                print ":( "
