import json

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from apps.enrollment.courses.models import *
from apps.enrollment.records.models import *

from apps.enrollment.courses.exceptions import NonCourseException
from apps.users.models import BaseUser, OpeningTimesView

import logging
from django.conf import settings
logger = logging.getLogger()


def main(request):
    return render(request, 'enrollment/main.html')


def get_courses_list_in_semester_with_history_info(user, semester):
    """
        This ugly piece of SQL is generally the
        fastest way to implement the functionality we want, so it's here
        as an exception.

        Disabled for now because the clients-side part isn't ready anyway.
        TODO: re-enable when that's done.
    """
    return Course.visible.filter(semester=semester)
    """
        .extra(select={'in_history': 'SELECT COUNT(*) FROM "records_record"' \
                                     ' INNER JOIN "courses_group" ON ("records_record"."group_id" = "courses_group"."id")' \
                                     ' INNER JOIN "courses_course" cc ON ("courses_group"."course_id" = cc."id")' \
                                     ' WHERE (cc."entity_id" = "courses_course"."entity_id"  AND "records_record"."student_id" = '+ str(user.student.id)+ '' \
                                     ' AND "records_record"."status" = \'1\' AND "cc"."semester_id" <> "courses_course"."semester_id")'})
    """


def get_course_list_info_json_for_semester(user, semester):
    if BaseUser.is_student(user):
        courses = get_courses_list_in_semester_with_history_info(
            user, semester)
    else:
        courses = Course.visible.filter(semester=semester)\
                                .order_by('entity__name')
    courses_list_for_json = [c.serialize_for_json() for c in courses]
    semester_for_json = {
        "id": semester.pk,
        "year": semester.year,
        "type": semester.get_type_display()
    }
    courses_list_info = {
        "courseList": courses_list_for_json,
        "semesterInfo": semester_for_json
    }
    return json.dumps(courses_list_info)


def prepare_courses_list_to_render(
        request, default_semester=None, user=None, student=None):
    ''' generates template data for filtering and list of courses '''
    if not default_semester:
        default_semester = Semester.get_default_semester()
    if not user:
        user = request.user
    semesters = Semester.objects.filter(visible=True)
    courses_list_json = get_course_list_info_json_for_semester(
        user, default_semester)
    return {
        'courses_list_json': courses_list_json,
        'semester_courses': semesters,
        'types_list': Type.get_all_for_jsfilter(),
        'default_semester': default_semester,
        'effects': Effects.objects.all(),
        'tags': Tag.objects.all(),
    }


def prepare_courses_list_to_render_and_return_course(
        request,
        default_semester=None,
        user=None,
        student=None,
        course_slug=None):
    ''' generates template data for filtering and list of courses '''
    render_data = prepare_courses_list_to_render(request, default_semester, user, student)
    result_course = None
    if course_slug:
        try:
            result_course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            pass
    return render_data, result_course


def courses(request):
    return render(
        request,
        'enrollment/courses/courses_list.html',
        prepare_courses_list_to_render(request))


def get_semester_info(request, semester_id):
    try:
        semesterObj = Semester.objects.get(
            Q(pk=semester_id) & Q(visible=True))
        jsonString = get_course_list_info_json_for_semester(
            request.user, semesterObj)

        return HttpResponse(jsonString, content_type='application/json')
    except Semester.DoesNotExist:
        raise Http404


def course(request, slug):
    try:
        default_semester = Semester.get_default_semester()
        user = request.user

        # Sprawdzamy, czy mamy studenta
        if user.is_anonymous():
            student = None
            student_id = 0
        else:
            if BaseUser.is_student(user):
                student = user.student
                student_id = student.id

            else:
                student = None
                student_id = 0

        data, course = prepare_courses_list_to_render_and_return_course(
            request, default_semester=default_semester, user=user, student=student, course_slug=slug)
        if student:
            try:
                t0 = OpeningTimesView.objects.get(student=student, course=course)
            except ObjectDoesNotExist:
                t0 = None
        else:
            t0 = None

        #course = list(Course.visible.filter(slug=slug).select_related('semester','entity'))
        if not course:
            raise Course.DoesNotExist

        course.teachers_list = course.teachers.all()  # potencjalnie problem z n zapytaniami do bazy

        groups = list(
            Group.objects.filter(
                course=course). extra(
                {
                    'priority': "SELECT COALESCE((SELECT priority FROM records_queue WHERE courses_group.id=records_queue.group_id AND records_queue.student_id=%s AND records_queue.deleted = false),0)" % (student_id,
                                                                                                                                                                                                             ),
                    'signed': "SELECT COALESCE((SELECT id FROM records_record WHERE courses_group.id=records_record.group_id AND status='%s' AND records_record.student_id=%s),0)" % (Record.STATUS_ENROLLED,
                                                                                                                                                                                      student_id)}). select_related(
                'teacher',
                'teacher__user'))

        # TODO: zrobić sortowanie groups w pythonie po terminach

        # Póki co można to usunąć, bo nie ma wymagań w systemie i będzie tu
        # problem n zapytań -> trzeba napisać sql ręcznie
        requirements = []
        #requirements = map(lambda x: x.name, course.requirements.all())

        if not student:
            course.is_recording_open = False
            for g in groups:
                g.is_in_diff = False
                g.signed = False
            pass
        else:
            enrolled_pinned_queued_ids_sql = """
            SELECT
                array(SELECT group_id FROM records_record WHERE status=%s AND records_record.student_id=%s) AS enrolled_ids,
                array(SELECT group_id FROM records_record WHERE status=%s AND records_record.student_id=%s) AS pinned_ids,
                array(SELECT group_id FROM records_queue WHERE records_queue.student_id=%s AND records_queue.deleted = false) AS queued_ids
            """
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(
                enrolled_pinned_queued_ids_sql, [
                    Record.STATUS_ENROLLED, student_id, Record.STATUS_PINNED, student_id, student_id])
            (enrolled_ids, pinned_ids, queued_ids) = cursor.fetchall()[0]

            queued = Queue.queued.filter(
                group__course=course, deleted=False).values(
                'priority', 'group_id')
            queue_priorities = Queue.queue_priorities_map_values(queued)

            course.can_enroll_from = course.get_enrollment_opening_time(student)
            course.is_recording_open = course.is_recording_open_for_student(student)
            if course.can_enroll_from:
                course.can_enroll_interval = course.can_enroll_from - datetime.now()

            for g in groups:
                # TODO to poniżej
                #g.is_in_diff = [group.id for group in student_groups if group.type == g.type]
                g.serialized = json.dumps(g.serialize_for_json(
                    enrolled_ids, queued_ids, pinned_ids,
                    queue_priorities, student
                ))

        lectures = []
        exercises = []
        laboratories = []
        exercises_adv = []
        exer_labs = []
        seminar = []
        language = []
        sport = []
        repertory = []
        project = []

        groups_ids = [g.id for g in groups]

        # Tworzymy listę słownik terminów(term_list: group_id -> [terminy jako
        # stringi])   ....jedno zapytanie sql
        terms_list = {}
        terms_list_get = terms_list.get
        terms_list_setdefault = terms_list.setdefault
        terms = Term.get_groups_terms(groups_ids)
        for term in terms:
            terms_list_setdefault(term['group_id'], []).append(term['term_as_string'])

        for g in groups:
            g.terms_list = terms_list_get(g.id, [])
            if student:
                g.is_full = g.is_full_for_student(student)
            else:
                g.is_full = False

            if g.type == '1':  # faster in good case, bad case - same
                lectures.append(g)
            elif g.type == '2':
                exercises.append(g)
            elif g.type == '3':
                laboratories.append(g)
            elif g.type == '4':
                exercises_adv.append(g)
            elif g.type == '5':
                exer_labs.append(g)
            elif g.type == '6':
                seminar.append(g)
            elif g.type == '7':
                language.append(g)
            elif g.type == '8':
                sport.append(g)
            elif g.type == '9':
                repertory.append(g)
            elif g.type == '10':
                project.append(g)
            else:
                break

        # Statystyki wyświetlane tylko adminom (nieadmin -> 0 zapytań sql, admin -> 1 zapytanie sql)
        statistics = {}
        for group_type in range(1, 11):
            statistics[str(group_type)] = {"in_group": 0, "in_queue": 0}

        if request.user.is_staff:
            from django.db import connection
            cursor = connection.cursor()
            statistics_sql = """
                SELECT type, SUM(s), COUNT(s) FROM
                (
                    SELECT type, student_id, MAX(rodzaj) as s FROM
                    (
                            SELECT records_record.student_id, courses_group."type", 1 as rodzaj FROM courses_group
                            JOIN records_record ON (records_record.group_id = courses_group.id)
                            WHERE records_record.status = '1' AND courses_group.course_id = %s
                        UNION
                            SELECT DISTINCT records_queue.student_id, courses_group."type", 0 as rodzaj FROM courses_group
                            JOIN records_queue ON (records_queue.group_id = courses_group.id)
                            WHERE courses_group.course_id = %s
                    ) AS r
                    GROUP BY type, student_id
                ) AS p
                GROUP BY type
            """
            cursor.execute(statistics_sql, [course.id, course.id])
            for row in cursor.fetchall():
                try:
                    statistics[str(row[0])] = {"in_group": row[1], "in_queue": row[2] - row[1]}
                except BaseException:
                    pass

        tutorials = [
            {'name': 'Wykłady', 'groups': lectures, 'type': 1, 'statistics': statistics['1']},
            {'name': 'Repetytorium', 'groups': repertory, 'type': 9, 'statistics': statistics['9']},
            {'name': 'Ćwiczenia', 'groups': exercises, 'type': 2, 'statistics': statistics['2']},
            {'name': 'Pracownia', 'groups': laboratories, 'type': 3, 'statistics': statistics['3']},
            {'name': 'Ćwiczenia (poziom zaawansowany)', 'groups': exercises_adv, 'type': 4, 'statistics': statistics['4']},
            {'name': 'Ćwiczenio-pracownie', 'groups': exer_labs, 'type': 5, 'statistics': statistics['5']},
            {'name': 'Seminarium', 'groups': seminar, 'type': 6, 'statistics': statistics['6']},
            {'name': 'Lektorat', 'groups': language, 'type': 7, 'statistics': statistics['7']},
            {'name': 'Zajęcia sportowe', 'groups': sport, 'type': 8, 'statistics': statistics['8']},
            {'name': 'Projekt', 'groups': project, 'type': 10, 'statistics': statistics['10']},
        ]

        courseView_details_hidden = request.COOKIES.get(
            'CourseView-details-hidden', False) == 'true'

        ectsLimitExceeded = False
        maxEcts = default_semester.get_current_limit()
        currentEcts = 0

        if student and student.get_points_with_course(course) > maxEcts:
            currentEcts = student.get_points()
            ectsLimitExceeded = True

        employees = {group.teacher for group in Group.objects.filter(course=course)}

        data.update({
            'details_hidden': courseView_details_hidden,
            'course': course,
            'employees': employees,
            'points': course.get_points(student),
            'tutorials': tutorials,
            'priority_limit': settings.QUEUE_PRIORITY_LIMIT,
            'requirements': requirements,
            't0': t0,
            'can_remove_record': default_semester.can_remove_record(),
            'ects_limit_would_be_exceeded': ectsLimitExceeded,
            'max_ects': maxEcts,
            'current_ects': currentEcts
        })

        if request.is_ajax():
            rendered_html = render_to_string(
                'enrollment/courses/course_info.html',
                data, request)
            return JsonResponse({
                'courseHtml': rendered_html,
                'courseName': course.name,
                'courseEditLink': reverse('admin:courses_course_change', args=[course.pk])
            })
        else:
            return render(request, 'enrollment/courses/course.html', data)

    except (Course.DoesNotExist, NonCourseException):
        raise Http404
