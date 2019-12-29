import json
from .helpers import auto_assign


# class MetaModel(type):
#     def __new__(cls, name, bases, attrs):
#         def init(self, **kwargs):
#             if not kwargs.keys() == set(self.fields):
#                 raise AttributeError()
#             self.__dict__.update(kwargs)
#             print("gituwa")

#         attrs['__init__'] = init
#         return super(MetaModel, cls).__new__(cls, name, bases, attrs)


class Model:
    # __metaclass__ = MetaModel

    @classmethod
    def from_json(cls, json_obj):
        dict_ = json.loads(json_obj)
        cls.from_dict(dict_)

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    def to_dict(self):
        """Convert model to dict recursively"""
        data = {}
        for key, value in self.__dict__.items():
            try:
                data[key] = value.to_dict()
            except AttributeError:
                data[key] = value
        return data

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


# TODO: change these models to dataclasses after upgrading to python >= 3.7
class Semester(Model):

    redirect_key = "semesters"
    is_paginated = False

    def __init__(self, id, display_name, year, type, usos_kod):
        self.id = id
        self.display_name = display_name
        self.year = year
        self.type = type
        self.usos_kod = usos_kod


class User(Model):
    """
    This model is used as nested object in some of other models.
    """

    def __init__(self, id, username, first_name, last_name):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class Student(Model):

    redirect_key = "students"
    is_paginated = True

    def __init__(self, id, matricula, ects,
                 status, user: dict, usos_id):
        self.id = id
        self.matricula = matricula
        self.ects = ects
        self.status = status
        self.user = User.from_dict(user)
        self.usos_id = usos_id


class Employee(Model):
    redirect_key = "employees"
    is_paginated = False

    def __init__(self, id, user: dict, consultations,
                 homepage, room, title, usos_id):
        self.id = id
        self.user = User.from_dict(user)
        self.consultations = consultations
        self.homepage = homepage
        self.room = room
        self.title = title
        self.usos_id = usos_id


class CourseInstance(Model):
    redirect_key = "courses"
    is_paginated = True

    @auto_assign
    def __init__(self, id, name, short_name, points, has_exam,
                 description, semester, course_type, usos_kod):
        pass


class Classroom(Model):
    redirect_key = "classrooms"
    is_paginated = False

    @auto_assign
    def __init__(self, id, type, description, number, order, building,
                 capacity, floor, can_reserve, slug, usos_id):
        pass


class Group(Model):
    redirect_key = "groups"
    is_paginated = True

    @auto_assign
    def __init__(self, id, type, course, teacher, limit, usos_nr):
        pass


class Record(Model):
    redirect_key = "records"
    is_paginated = True

    @auto_assign
    def __init__(self, id, group, student):
        pass


class Desiderata(Model):
    redirect_key = "desideratas"
    is_paginated = True

    @auto_assign
    def __init__(self, id, day, hour, employee, semester):
        pass


class DesiderataOther(Model):
    redirect_key = "desiderata-others"
    is_paginated = True

    @auto_assign
    def __init__(self, id, comment, employee, semester):
        pass


class SpecialReservation(Model):
    redirect_key = "special-reservation"
    is_paginated = True

    @auto_assign
    def __init__(self, id, title, DayOfWeek, start_time,
                 end_time, semester, classroom):
        pass


class SystemState(Model):
    redirect_key = "systemstate"
    is_paginated = False

    @auto_assign
    def __init__(self, id, state_name):
        pass


class SingleVote(Model):
    redirect_key = "votes"
    is_paginated = True

    @auto_assign
    def __init__(self, student, course_name, vote_points):
        pass


class Term(Model):
    redirect_key = "terms"
    is_paginated = True

    @auto_assign
    def __init__(self, id, dayOfWeek, start_time, end_time,
                 group, classrooms, usos_id):
        pass
