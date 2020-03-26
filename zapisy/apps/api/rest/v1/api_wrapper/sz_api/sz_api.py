import json
import requests
from urllib.parse import urljoin, urlparse
from typing import Iterator, Optional

from .models import (User, Program,
                     Semester, Student,
                     Employee, CourseInstance,
                     Classroom, Group,
                     Term, Record,
                     Desiderata, DesiderataOther,
                     SpecialReservation, SystemState,
                     SingleVote, Model)


class ZapisyApi:
    """Wrapper for github.com/iiuni/projektzapisy rest api.

    Initializer of ZapisyApi object takes:
        User token used for authenticating requests.
        Optional url pointing to projektzapisy.

    Example of use:
        from sz_api import ZapisyApi
        api = ZapisyApi(token='Token valid_key')
        for semester in api.semesters():
            semester.usos_kod = 123
            api.save(semester)

    Data retrieved from API is defined by models in model.py,
    wrapper can also save some data with save method.
    Not every field can be saved, wrapper will throw HTTPError
    if REST API rejects request. You can use apps/api/rest/v1/serializers.py
    in projektzapisy as additional reference.

    public methods raise:
        ValueError for error in decoding api response
        requests.exceptions.RequestException
            for errors during client-server communication
    """

    def __init__(self, token: str,
                 api_url: str = "https://zapisy.ii.uni.wroc.pl/api/v1/"):
        self.token = token
        self.redirect_map = self._get_redirect_map(api_url)

    def _get_redirect_map(self, api_url: str) -> dict:
        rm = self._handle_get_request(api_url)
        base_url_parts = urlparse(api_url)
        for key in rm:
            route_url_parts = urlparse(rm[key])
            modified_url_parts = route_url_parts._replace(scheme=base_url_parts.scheme)
            rm[key] = modified_url_parts.geturl()
        return rm

    def save(self, obj: Model):
        self._handle_patch_request(
            urljoin(self.redirect_map[obj.redirect_key], str(obj.id)),
            data=obj.to_dict()
        )

    def semesters(self) -> Iterator[Semester]:
        """Returns an iterator over Semester objects."""
        return self._get_deserialized_data(Semester)

    def semester(self, id: int) -> Semester:
        """Returns Semester with a given id."""
        return self._get_single_record(Semester, id)

    def current_semester(self) -> Optional[Semester]:
        """Returns current semester or None."""
        return self._action(Semester, "current")

    def students(self) -> Iterator[Student]:
        """Returns an iterator over Student objects."""
        return self._get_deserialized_data(Student)

    def student(self, id: int) -> Student:
        """Returns Student with a given id."""
        return self._get_single_record(Student, id)

    def employees(self) -> Iterator[Employee]:
        """Returns an iterator over Employee objects."""
        return self._get_deserialized_data(Employee)

    def employee(self, id: int) -> Employee:
        """returns Employee with a given id."""
        return self._get_single_record(Employee, id)

    def courses(
        self, semester_id: Optional[int] = None
    ) -> Iterator[CourseInstance]:
        """Returns an iterator over courses.

        Args:
            semester_id: Only courses for the semester are listed if provided.
        """
        return self._get_deserialized_data(
            CourseInstance, params={"semester_id": semester_id})

    def course(self, id: int) -> CourseInstance:
        """Returns course with a given id."""
        return self._get_single_record(CourseInstance, id)

    def classrooms(self) -> Iterator[Classroom]:
        """Returns an iterator over classrooms."""
        return self._get_deserialized_data(Classroom)

    def classroom(self, id: int) -> Classroom:
        """Returns classroom with a given id."""
        return self._get_single_record(Classroom, id)

    def groups(self, course_id: Optional[int] = None) -> Iterator[Group]:
        """Returns an iterator over course groups.

        If `course` parameter is provided, only lists groups for this course.
        """
        return self._get_deserialized_data(
            Group, params={"course_id": course_id})

    def group(self, id: int) -> Group:
        """Returns group with a given id."""
        return self._get_single_record(Group, id)

    def terms(self, semester_id: Optional[int] = None) -> Iterator[Term]:
        """Returns an iterator over group terms.

        Term represents a single meeting between the teacher and the students
        in a week. A group may have multiple terms, typically this happens
        only for lecture groups.
        Args:
            semester_id: If provided, only terms in the semester are listed.
        """
        return self._get_deserialized_data(
            Term, params={"group__course__semester": semester_id})

    def term(self, id: int) -> Term:
        """Returns term with a given id"""
        return self._get_single_record(Term, id)

    def records(
        self,
    ) -> Iterator[Record]:
        """Lists enrolment records."""
        return self._get_deserialized_data(Record)

    def record(self, id: int) -> Record:
        """Returns the Record with a given id."""
        return self._get_single_record(Record, id)

    def desideratas(
        self, filters: Optional[dict] = None
    ) -> Iterator[Desiderata]:
        """Lists Employees' desideratas.

        Desiderata is a teacher's statement of willingness to teach at certain
        hours of the week. Filtering by any field is possible by passing it in
        `filters` dict.
        """
        return self._get_deserialized_data(Desiderata, params=filters)

    def desiderata(self, id: int) -> Desiderata:
        """Returns desiderata with a given id."""
        return self._get_single_record(Desiderata, id)

    def desiderata_others(
        self, filters: Optional[dict] = None
    ) -> Iterator[DesiderataOther]:
        """Lists DesiderataOther objects.

        DesiderataOther plays a similar role to that of Desiderata, except it
        is a written statement rather than structured. Filtering by any field
        is possible by passing it in `filters` dict.
        """
        return self._get_deserialized_data(DesiderataOther, params=filters)

    def desiderata_other(self, id: int) -> DesiderataOther:
        """Returns DesiderataOther object with a given id."""
        return self._get_single_record(DesiderataOther, id)

    def special_reservations(
        self, filters: Optional[dict] = None
    ) -> Iterator[SpecialReservation]:
        """Lists SpecialReservation objects.

        SpecialReservation is a way to book a room for a semester. Filtering
        by any field is possible by passing it in `filters` dict.
        """
        return self._get_deserialized_data(SpecialReservation, params=filters)

    def special_reservation(self, id: int) -> SpecialReservation:
        """Returns SpecialReservation object with a given id."""
        return self._get_single_record(SpecialReservation, id)

    def single_votes(
        self, filters: Optional[dict] = None
    ) -> Iterator[SingleVote]:
        """Iterates over SingleVote objects.

        Votes with value = 0 are ignored. Filtering by `state` (academic
        year) is recommended. Filtering by any other field is possible.
        """
        return self._get_deserialized_data(SingleVote, params=filters)

    def systemstates(
        self, filters: Optional[dict] = None
    ) -> Iterator[SystemState]:
        """Lists SystemState objects.

        Filtering by any field is possible by passing it in `filters` dict.
        """
        return self._get_deserialized_data(SystemState, params=filters)

    def systemstate(self, id: int) -> SystemState:
        """Returns the SystemState object with a given id"""
        return self._get_single_record(SystemState, id)

    def create_student(self, usos_id, indeks, first_name, last_name, email,
                       ects, program_name, semestr) -> int:
        """Adds new student in the Enrolment System and returns its id."""
        student = Student(
            None, usos_id, indeks, ects, True,
            User(None, str(indeks), first_name, last_name, email),
            Program(None, program_name), semestr)
        resp = self._handle_post_request(
            self.redirect_map[Student.redirect_key], student.to_dict())
        return resp.json()['id']

    def _get_deserialized_data(self, model_class, params=None):
        if model_class.is_paginated:
            data_gen = self._get_paginated_data(model_class, params)
        else:
            data_gen = self._get_unpaginated_data(model_class, params)
        yield from map(model_class.from_dict, data_gen)

    def _get_paginated_data(self, model_class, params):
        response = self._handle_get_request(
            self.redirect_map[model_class.redirect_key], params)
        yield from iter(response["results"])

        while response["next"] is not None:
            response = self._handle_get_request(response["next"], params)
            yield from iter(response["results"])

    def _get_unpaginated_data(self, model_class, params):
        yield from iter(self._handle_get_request(
            self.redirect_map[model_class.redirect_key], params))

    def _get_single_record(self, model_class, name):
        return model_class.from_dict(
            self._handle_get_request(
                urljoin(self.redirect_map[model_class.redirect_key], str(name))
            )
        )

    def _action(self, model_class, name):
        resp = self._handle_get_request(
            urljoin(self.redirect_map[model_class.redirect_key], str(name))
        )

        if resp is not None:
            return model_class.from_dict(resp)
        else:
            return resp

    def _handle_get_request(self, path, params=None):
        """Sends GET request to API and returns json response.

        Raises:
            sz_api.ApiError: When response decoding fails.
            requests.exceptions.RequestException
        """
        params = dict() if params is None else params

        resp = requests.get(
            path,
            headers={"Authorization": self.token},
            # filter out None params
            params={k: v for k, v in params.items() if v is not None}
        )
        resp.raise_for_status()
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            return None

    def _handle_patch_request(self, path, data: dict):
        return self._handle_upload_request("patch", path, data)

    def _handle_post_request(self, path, data: dict):
        return self._handle_upload_request("post", path, data)

    def _handle_upload_request(self, method, path, data: dict):
        """Sends PATCH or POST request to API.

        Raises:
            requests.exceptions.RequestException
            ValueError
        """
        if method == 'patch':
            func = requests.patch
        elif method == 'post':
            func = requests.post
        else:
            raise ValueError()

        resp = func(
            # DRF requires trailing slash for patch method
            path if path.endswith("/") else path + "/",
            json=data,
            headers={"Authorization": self.token})
        resp.raise_for_status()
        return resp
