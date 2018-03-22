from mailer.models import Message
from apps.enrollment.courses.models import Semester
from apps.enrollment.records.models import Record
from apps.users.models import Employee, Student


def run():
    students = Student.objects.filter(status=0)
    current_semester = Semester.get_current_semester()
    counter = 0
    for student in students:
        address = student.user.email
        ids = Record.get_student_records_ids(student, current_semester)
        if (address and len(ids['enrolled']) > 0) or address == 'lewymati@wp.pl':
            body = "Witaj, \n\ninformujemy, że jutro kończy się ocena zajęć. Przypominamy, że udział w ocenie zajęć daje bonus 24h do otwarcia zapisów w następnym roku akademickim.\n\nZespół zapisy.ii.uni.wroc.pl\n\n---\nWiadomość została wygenerowana automatycznie, prosimy na nią nie odpowiadać."
            subject = '[Zapisy] Przypomnienie o ocenie zajęć'
            counter += 1
            Message.objects.create(
                to_address=address,
                from_address='zapisy@cs.uni.wroc.pl',
                subject=subject,
                message_body=body)
    print(counter)
