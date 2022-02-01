import json

from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.course_type import Type
from apps.offer.proposal.models import Proposal
from apps.users.models import Program

mapper = {'effect': Effects, 'tag': Tag, 'type': Type, 'subject': Proposal}


def load_requirements_file():
    with open('wymagania.json') as json_file:
        data = json.load(json_file)
    return data


def program_exists(data, program):
    return str(program) in data.keys()


def load_list_of_programs_and_years(data):
    res = dict()

    programs = Program.objects.filter(id__in=data.keys())

    for program in programs:
        res[program] = dict()
        res[program]['years'] = list(data[str(program.id)].keys())
        res[program]['id'] = str(program.id)

    return res


def load_studies_requirements(data, program, starting_year=2019):
    program_requirements = data[str(program)]

    year = proper_year_for_program(data, program, starting_year)

    return program_requirements[year]


def proper_year_for_program(data, program, year):
    program_requirements = data[str(program)]

    years = program_requirements.keys()
    years_lower = [x for x in years if int(x) <= year]

    if years_lower:
        year = max(years_lower)
    else:
        year = max(years)

    return year


def requirements(data, program, starting_year=2019):
    reqs = load_studies_requirements(data, program, starting_year)
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

        if 'groupBy' in value.keys():
            res[key]['groupBy'] = value['groupBy']

        if 'aggregate' in value.keys():
            res[key]['aggregate'] = value['aggregate']

    return res


def get_all_points(filterNot, limit, completed_courses):
    sum = 0

    filtered_courses = completed_courses

    for table, objects in filterNot.items():
        if table == 'subject':
            filtered_courses = [
                record for record in filtered_courses if record.course.offer not in objects
            ]
        if table == 'type':
            filtered_courses = [
                record for record in filtered_courses if record.course.course_type not in objects
            ]

    if 'type' not in limit:
        limit['type'] = {}

    used_limits = {}

    for type in limit['type']:
        used_limits[type] = 0

    for record in filtered_courses:
        course = record.course
        type = course.course_type
        if type in limit['type']:
            added_sum = min(limit['type'][type] - used_limits[type], course.points)
            used_limits[type] += added_sum
            sum += added_sum
        else:
            sum += course.points

    return sum


def get_points_sum(filter, limit, completed_courses):
    sum = 0
    if 'type' not in limit:
        limit['type'] = {}

    used_limits = {}

    for type in limit['type']:
        used_limits[type] = 0

    for record in completed_courses:
        course = record.course
        for table, objects in filter.items():
            if table == 'subject':
                if course.offer in objects:
                    sum += course.points
            elif table == 'type':
                type = course.course_type
                if type in objects:
                    if type in limit['type']:
                        added_sum = min(limit['type'][type] - used_limits[type], course.points)
                        used_limits[type] += added_sum
                        sum += added_sum
                    else:
                        sum += course.points
            elif table == 'effect':
                if not set([effect for effect in course.effects.all()]).isdisjoint(set(objects)):
                    sum += course.points
            elif table == 'tag':
                if not set([tag for tag in course.tags.all()]).isdisjoint(set(objects)):
                    sum += course.points

    return sum


def is_passed(filter, completed_courses):
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
