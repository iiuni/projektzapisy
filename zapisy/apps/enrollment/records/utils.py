# -*- coding: utf-8 -*-
import json

from django.db.models.query import QuerySet
from django.conf import settings
from apps.enrollment.courses.models import Term
from apps.enrollment.records.models import *
from apps.users.models import *


def run_rearanged(result, group=None):
    def test_course(group):
        import datetime
        if isinstance(group, Record):
            course = group.group.course
        elif isinstance(group, Group):
            course = group.course

        semester = course.semester
        now = datetime.datetime.now()

        if semester.records_closing < now or not (
                course.records_start and course.records_end and course.records_start <= now < course.records_end):
            return False

        return True

    if isinstance(result, QuerySet) and test_course(result[0]):
        for g in result:
            Group.do_rearanged(g.group)

    elif isinstance(result, Group) and test_course(result):
        Group.do_rearanged(result)

    if group and group.should_be_rearranged():
        Group.do_rearanged(group)


def prepare_courses_with_terms(terms=None, records=None):
    if records is None:
        records = []

    if terms is None:
        default_semester = Semester.objects.get_next()
        if not default_semester:
            return []
        terms = Term.get_all_in_semester(default_semester)

    courses_terms_map = {}
    for term in terms:
        course = term.group.course
        if course not in courses_terms_map:
            courses_terms_map[course] = []
        courses_terms_map[course].append(term)

    for record in records:
        if record.group.course not in courses_terms_map:
            courses_terms_map[record.group.course] = []

    courses = [(course, terms) for course, terms in courses_terms_map.items()]

    return sorted(courses, key=lambda item: item[0].name)


def prepare_groups_json(semester, groups, student=None, employee=None):
    record_ids = Record.get_student_records_ids(student, semester)
    if student:
        queue_priorities = Queue.queue_priorities_map(
            Queue.get_student_queues(student, semester))
    else:
        queue_priorities = {}
    groups_json = []
    for group in groups:
        groups_json.append(group.serialize_for_json(
            record_ids['enrolled'], record_ids['queued'], record_ids['pinned'],
            queue_priorities, student=student, employee=employee
        ))
    return json.dumps(groups_json)


def prepare_courses_json(groups, student):
    courses_json = []
    for group in groups:
        courses_json.append(group.course.serialize_for_json(student))
    return json.dumps(courses_json)


def prepare_schedule_courses(request, for_student=None, for_employee=None, semester=None):
    if not (for_student is None) and not (for_employee is None):
        raise RuntimeError('Nie można wygenerować jednocześnie dla studenta' +
                           ' i pracownika')

    default_semester = semester or Semester.objects.get_next()

    if for_employee is not None:
        terms = Term.get_all_in_semester(default_semester, employee=for_employee)
    else:
        terms = Term.get_all_in_semester(default_semester, student=for_student)

    try:
        if BaseUser.is_student(request.user):
            records = Record.get_student_enrolled_objects(request.user.student,
                                                          default_semester)
        else:
            records = []
    except Student.DoesNotExist:
        records = []

    return prepare_courses_with_terms(terms=terms, records=records)


def prepare_schedule_data(request, courses, semester=None):
    if BaseUser.is_student(request.user):
        student = request.user.student
    else:
        student = None
    if BaseUser.is_employee(request.user):
        employee = request.user.employee
    else:
        employee = None
    default_semester = semester or Semester.objects.get_next()

    terms_by_days = [None for i in range(8)]  # dni numerowane od 1
    for item in courses:
        for term in item[1]:
            day = int(term.dayOfWeek)
            if not terms_by_days[day]:
                terms_by_days[day] = {
                    'day_id': day,
                    'day_name': term.get_dayOfWeek_display(),
                    'terms': []
                }
            oldTerm = term
            term = {}
            term['object'] = oldTerm
            term['json'] = json.dumps(term['object'].serialize_for_json())
            terms_by_days[day]['terms'].append(term)
    terms_by_days = filter(lambda term: term, terms_by_days)

    # TODO: tylko grupy, na które jest zapisany
    all_groups = Group.get_groups_by_semester(default_semester)
    all_groups_json = prepare_groups_json(default_semester, all_groups,
                                          student=student, employee=employee)

    return {
        'courses_json': prepare_courses_json(all_groups, student),
        'groups_json': all_groups_json,
        'terms_by_days': terms_by_days,
        'priority_limit': settings.QUEUE_PRIORITY_LIMIT,
    }


import csv
import codecs
import cStringIO


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
