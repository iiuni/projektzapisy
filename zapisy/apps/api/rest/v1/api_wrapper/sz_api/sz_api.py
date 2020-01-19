import json
import requests
from urllib.parse import urljoin
from typing import Iterator, Optional

from .models import (Semester, Student,
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
        return self._handle_get_request(api_url)

    def save(self, obj: Model):
        self._handle_patch_request(
            urljoin(self.redirect_map[obj.redirect_key], str(obj.id)),
            data=obj.to_dict()
        )

    def semesters(
        self, visible: Optional[bool] = None
    ) -> Iterator[Semester]:
        """Returns iterator over Semester objects.

        If visible parameter is provided, filters results by its value
        """
        return self._get_deserialized_data(Semester, {"visible": visible})

    def semester(self, id: int) -> Semester:
        """Returns Semester with given id"""
        return self._get_single_record(Semester, id)

    def current_semester(self) -> Optional[Semester]:
        """If exist, it returns current semester. otherwise return None"""
        return self._action(Semester, "current")

    def students(self) -> Iterator[Student]:
        """Gets an iterator over Student objects"""
        return self._get_deserialized_data(Student)

    def student(self, id: int) -> Student:
        """Returns Student with given id"""
        return self._get_single_record(Student, id)

    def employees(self) -> Iterator[Employee]:
        """Gets an iterator over Employee objects"""
        return self._get_deserialized_data(Employee)

    def employee(self, id: int) -> Employee:
        """returns Employee with given id"""
        return self._get_single_record(Employee, id)

    def courses(
        self, semester_id: Optional[int] = None
    ) -> Iterator[CourseInstance]:
        """Gets an iterator over courses"""
        return self._get_deserialized_data(
            CourseInstance, params={"semester_id": semester_id})

    def course(self, id: int) -> CourseInstance:
        """returns course with given id"""
        return self._get_single_record(CourseInstance, id)

    def classrooms(self) -> Iterator[Classroom]:
        """Returns an iterator over classrooms"""
        return self._get_deserialized_data(Classroom)

    def classroom(self, id: int) -> Classroom:
        """Returns classroom with given id"""
        return self._get_single_record(Classroom, id)

    def groups(self, course_id: Optional[int] = None) -> Iterator[Group]:
        """Gets an iterator over groups

        If `course` parameter is provided, filters results by its value
        """
        return self._get_deserialized_data(
            Group, params={"course_id": course_id})

    def group(self, id: int) -> Group:
        """Returns group with given id"""
        return self._get_single_record(Group, id)

    def terms(self, semester_id: Optional[int] = None) -> Iterator[Term]:
        """Gets an iterator over groups

        If `semester_id` parameter is provided, filters results by its value
        """
        return self._get_deserialized_data(
            Term, params={"group__course__semester": semester_id})

    def term(self, id: int) -> Term:
        """Returns term with given id"""
        return self._get_single_record(Term, id)

    def records(
        self,
    ) -> Iterator[Record]:
        """Gets an iterator over enrolled records
        """
        return self._get_deserialized_data(Record)

    def record(self, id: int) -> Record:
        """Returns term with given id"""
        return self._get_single_record(Record, id)

    def desideratas(
        self, filters: Optional[dict] = None
    ) -> Iterator[Desiderata]:
        """Gets an iterator over desideratas.

        Filtering by any field is possible by passing it in `filters` dict
        """
        return self._get_deserialized_data(Desiderata, params=filters)

    def desiderata(self, id: int) -> Desiderata:
        """Returns desiderata with given id"""
        return self._get_single_record(Desiderata, id)

    def desiderata_others(
        self, filters: Optional[dict] = None
    ) -> Iterator[DesiderataOther]:
        """Gets an iterator over DesiderataOther objects.

        Filtering by any field is possible by passing it in `filters` dict
        """
        return self._get_deserialized_data(DesiderataOther, params=filters)

    def desiderata_other(self, id: int) -> DesiderataOther:
        """Returns DesiderataOther object with given id"""
        return self._get_single_record(DesiderataOther, id)

    def special_reservations(
        self, filters: Optional[dict] = None
    ) -> Iterator[SpecialReservation]:
        """Gets an iterator over SpecialReservation objects.

        Filtering by any field is possible by passing it in `filters` dict
        """
        return self._get_deserialized_data(SpecialReservation, params=filters)

    def special_reservation(self, id: int) -> SpecialReservation:
        """Returns desiderata with given id"""
        return self._get_single_record(SpecialReservation, id)

    def single_votes(
        self, filters: Optional[dict] = None
    ) -> Iterator[SingleVote]:
        """Gets an iterator over SingleVote objects.
        Votes with value = 0 are ignored.

        Filtering by any field is possible by passing it in `filters` dict.
        Filtering by `state` (SystemState) is also possible.
        """
        return self._get_deserialized_data(SingleVote, params=filters)

    def systemstates(
        self, filters: Optional[dict] = None
    ) -> Iterator[SystemState]:
        """Gets an iterator over SystemState objects.

        Filtering by any field is possible by passing it in `filters` dict.
        """
        return self._get_deserialized_data(SystemState, params=filters)

    def systemstate(self, id: int) -> SystemState:
        """Returns SystemState object with given id"""
        return self._get_single_record(SystemState, id)

    def post_usos_data(self, content: str):
        """Sends usos students data to database for migrating purposes"""
        self._handle_post_request(
            self.redirect_map["usos"], {"content": content})

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
        """sends GET request to api and return json response

        Raises:
            sz_api.ApiError for error in decoding response
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
        self._handle_upload_request("patch", path, data)

    def _handle_post_request(self, path, data: dict):
        self._handle_upload_request("post", path, data)

    def _handle_upload_request(self, method, path, data: dict):
        """sends PATCH or POST request to api

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
            data=data,
            headers={"Authorization": self.token}
        )
        resp.raise_for_status()
