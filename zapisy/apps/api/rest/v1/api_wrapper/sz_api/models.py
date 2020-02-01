from .helpers import auto_assign


class Model:
    """Base class representing Django models without database access.

    Models in this file reflect serializers in apps/api/rest/v1/serializers.py (projektzapisy).
    """

    @classmethod
    def from_dict(cls, obj):
        if type(obj) == cls or obj is None:
            return obj
        try:
            return cls(**obj)
        except TypeError:
            raise ModelInitalizationError(f"{cls.__name__}")

    def to_dict(self):
        """Converts model to dict recursively"""
        data = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            try:
                data[key] = value.to_dict()
            except AttributeError:
                data[key] = value
        return data

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class ModelInitalizationError(Exception):
    """Raised when Model initialization fails due to missing fields."""
    pass


class Semester(Model):

    redirect_key = "semesters"
    is_paginated = False

    @auto_assign
    def __init__(self, id, display_name, year, type, usos_kod):
        pass


class Program(Model):
    """Represents the study programme in the Enrolment System.

    This model is used as nested object in another model (Student).
    """
    @auto_assign
    def __init__(self, id, name):
        pass


class User(Model):
    """Represents user in the Enrollment System.

    This model is used as nested object in some of other models (Student, Employee).
    """
    @auto_assign
    def __init__(self, id, username, first_name, last_name, email):
        pass


class Student(Model):
    redirect_key = "students"
    is_paginated = True

    @auto_assign
    def __init__(self, id, usos_id, matricula, ects, status,
                 user: dict, program: dict, semestr, algorytmy_l,
                 numeryczna_l, dyskretna_l):
        self.user = User.from_dict(user)
        self.program = Program.from_dict(program)


class Employee(Model):
    redirect_key = "employees"
    is_paginated = False

    @auto_assign
    def __init__(self, id, user: dict, consultations,
                 homepage, room, title, usos_id):
        self.user = User.from_dict(user)


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
    def __init__(self, id, type, course, teacher, limit, human_readable_type,
                 teacher_full_name, export_usos, usos_nr):
        self.course = CourseInstance.from_dict(course)
        self.teacher = Employee.from_dict(teacher)


class Record(Model):
    redirect_key = "records"
    is_paginated = True

    @auto_assign
    def __init__(self, id, group, student):
        pass


class Desiderata(Model):
    redirect_key = "desideratas"
    is_paginated = False

    @auto_assign
    def __init__(self, id, day, hour, employee, semester):
        pass


class DesiderataOther(Model):
    redirect_key = "desiderata-others"
    is_paginated = False

    @auto_assign
    def __init__(self, id, comment, employee, semester):
        pass


class SpecialReservation(Model):
    redirect_key = "special-reservation"
    is_paginated = False

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
