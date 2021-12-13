import json

from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.course_type import Type
from apps.offer.proposal.models import Proposal

mapper = {'effect': Effects, 'tag': Tag, 'type': Type, 'subject': Proposal}


def load_studies_requirements(program, starting_year=2019):
    with open('wymagania.json') as json_file:
        data = json.load(json_file)

    program_requirements = data[str(program)]

    years = program_requirements.keys()
    years_lower = [x for x in years if int(x) <= starting_year]

    if years_lower:
        year = max(years_lower)
    else:
        year = max(years)

    return program_requirements[year]


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
                        try:
                            name = dao.objects.get(pk=id)
                        except:
                            print(f"Table: {table}, id: {id}")
                        res[key]['limit'][table][name] = ects

        if 'filter' in value.keys():
            filters = value['filter']
            res[key]['filter'] = dict()
            for table, ids in filters.items():
                if table in mapper.keys():
                    res[key]['filter'][table] = list()
                    dao = mapper[table]
                    for id in ids:
                        try:
                            name = dao.objects.get(pk=id)
                        except:
                            print(f"Table: {table}, dao: {dao}, id: {id}, key: {key}")
                        res[key]['filter'][table].append(name)

        if 'filterNot' in value.keys():
            filters = value['filterNot']
            res[key]['filterNot'] = dict()
            for table, ids in filters.items():
                if table in mapper.keys():
                    res[key]['filterNot'][table] = list()
                    dao = mapper[table]
                    for id in ids:
                        try:
                            name = dao.objects.get(pk=id)
                        except:
                            print(f"Table: {table}, id: {id}")
                        res[key]['filterNot'][table].append(name)

    return res
