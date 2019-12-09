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

    def __init__(self, id, username, first_name, last_name):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class Student(Model):

    redirect_key = "students"
    is_paginated = True

    def __init__(self, id, matricula, ects, status, user: dict, usos_id):
        self.id = id
        self.matricula = matricula
        self.ects = ects
        self.status = status
        self.user = User.from_dict(user)
        self.usos_id = usos_id
