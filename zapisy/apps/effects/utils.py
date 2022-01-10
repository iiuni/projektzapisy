import json

from apps.effects.models import CompletedCourses
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.course_type import Type
from apps.offer.proposal.models import Proposal
from apps.users.models import Program, Student

mapper = {'effect': Effects, 'tag': Tag, 'type': Type, 'subject': Proposal}


def load_requirements_file():
    with open('wymagania.json') as json_file:
        data = json.load(json_file)
    return data


def load_list_of_programs_and_years():
    data = load_requirements_file()

    res = dict()

    for program_id in data.keys():
        program = Program.objects.get(pk=program_id)

        res[program] = dict()
        res[program]['years'] = list(data[program_id].keys())
        res[program]['id'] = program_id

    return res


def load_studies_requirements(program, starting_year=2019):
    data = load_requirements_file()

    program_requirements = data[str(program)]

    years = program_requirements.keys()
    years_lower = [x for x in years if int(x) <= starting_year]

    if years_lower:
        year = max(years_lower)
    else:
        year = max(years)

    return program_requirements[year]


def proper_year_for_program(program, year):
    data = load_requirements_file()

    program_requirements = data[str(program)]

    years = program_requirements.keys()
    years_lower = [x for x in years if int(x) <= year]

    if years_lower:
        year = max(years_lower)
    else:
        year = max(years)

    return year


def requirements(program, starting_year=2019):
    reqs = load_studies_requirements(program, starting_year)
    res = dict()

    for key, value in reqs.items():
        res[key] = dict()
        res[key]['description'] = value['description']
        if 'sum' in value.keys():
            res[key]['sum'] = value['sum']

        if 'limit' in value.keys():
            limits = value['limit']
            res[key]['limit'] = dict()
            for table, ids in limits.items():
                if table in mapper.keys():
                    res[key]['limit'][table] = dict()
                    dao = mapper[table]
                    for id, ects in ids.items():
                        name = dao.objects.get(pk=id)
                        res[key]['limit'][table][name] = ects

        if 'filter' in value.keys():
            filters = value['filter']
            res[key]['filter'] = dict()
            for table, ids in filters.items():
                if table in mapper.keys():
                    res[key]['filter'][table] = list()
                    dao = mapper[table]
                    for id in ids:
                        name = dao.objects.get(pk=id)
                        res[key]['filter'][table].append(name)

        if 'filterNot' in value.keys():
            filters = value['filterNot']
            res[key]['filterNot'] = dict()
            for table, ids in filters.items():
                if table in mapper.keys():
                    res[key]['filterNot'][table] = list()
                    dao = mapper[table]
                    for id in ids:
                        name = dao.objects.get(pk=id)
                        res[key]['filterNot'][table].append(name)

    return res


def get_all_points(student_id):
    student = Student.objects.get(pk=student_id)
    completed_courses = (CompletedCourses.objects.filter(student=student, program=student.program))

    sum = 0

    for record in completed_courses:
        course = record.course
        sum += course.points

    return sum


def get_points_sum(student_id, filter):
    student = Student.objects.get(pk=student_id)
    completed_courses = (CompletedCourses.objects.filter(student=student, program=student.program))

    sum = 0

    for record in completed_courses:
        course = record.course
        for table, objects in filter.items():
            if table == 'subject':
                if course.offer in objects:
                    sum += course.points
            if table == 'type':
                if course.course_type in objects:
                    sum += course.points
            if table == 'effect':
                if not set([effect for effect in course.effects.all()]).isdisjoint(set(objects)):
                    sum += course.points
            if table == 'tag':
                if not set([tag for tag in course.tags.all()]).isdisjoint(set(objects)):
                    sum += course.points

    return sum


def is_passed(student_id, filter):
    student = Student.objects.get(pk=student_id)
    completed_courses = (CompletedCourses.objects.filter(student=student, program=student.program))

    passed = False

    for record in completed_courses:
        course = record.course
        for table, objects in filter.items():
            if table == 'subject':
                if course.offer in objects:
                    passed = True
                    break
            if table == 'type':
                if course.course_type in objects:
                    passed = True
                    break
            if table == 'effect':
                if not set([effect for effect in course.effects.all()]).isdisjoint(set(objects)):
                    passed = True
                    break
            if table == 'tag':
                if not set([tag for tag in course.tags.all()]).isdisjoint(set(objects)):
                    passed = True
                    break
        if passed:
            break

    return passed
