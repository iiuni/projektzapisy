import json


class Model:
    @classmethod
    def from_json(cls, json_obj):
        dict_ = json.loads(json_obj)
        cls.from_dict(dict_)

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)

    def _to_json(self):
        return json.dumps(self.__dict__)

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

    def __init__(self, id, name, short_name,
                 points, has_exam, description,
                 semester, course_type, usos_kod):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.points = points
        self.has_exam = has_exam
        self.description = description
        self.semester = semester
        self.course_type = course_type
        self.usos_kod = usos_kod
