import requests
from urllib.parse import urljoin
from typing import Iterator, Optional

from pprint import pprint

from .models import (Semester, Student,
                     Employee, CourseInstance,
                     Classroom, Model)


class ZapisyApi:
    """Wrapper for github.com/iiuni/projektzapisy rest api.

    Initializer of ZapisyApi object takes:
        User token used for authenticating requests.
        Optional url pointing to projektzapisy.

    Example of use:
        from sz_api import ZapisyApi
        api = ZapisyApi(token='Token valid_key')
        print(list(api.semesters()))

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
        """
        returns iterator over Semester objects.

        if visible parameter is provided, filters results by its value
        """
        return self._get_deserialized_data(Semester, {"visible": visible})

    def semester(self, id: int) -> Semester:
        """
        returns Semester with given id
        """
        return self._get_single_record(Semester, id)

    def students(self) -> Iterator[Student]:
        """
        Gets an iterator over Student objects
        """
        return self._get_deserialized_data(Student)

    def student(self, id: int) -> Student:
        """
        returns Student with given id
        """
        return self._get_single_record(Student, id)

    def employees(self) -> Iterator[Employee]:
        """
        Gets an iterator over Employee objects
        """
        return self._get_deserialized_data(Employee)

    def employee(self, id: int) -> Employee:
        """
        returns Employee with given id
        """
        return self._get_single_record(Employee, id)

    def courses(
        self, semester_id: Optional[int] = None
    ) -> Iterator[CourseInstance]:
        """
        Gets an iterator over courses
        """
        return self._get_deserialized_data(
            CourseInstance, params={"semester_id": semester_id})

    def course(self, id: int) -> CourseInstance:
        """
        returns course with given id
        """
        return self._get_single_record(CourseInstance, id)

    def classrooms(self) -> Iterator[Classroom]:
        """
        Returns an iterator over classrooms
        """
        return self._get_deserialized_data(Classroom)

    def classroom(self, id: int) -> Classroom:
        """
        Returns classroom with given id
        """
        return self._get_single_record(Classroom, id)

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

    def _get_single_record(self, model_class, id):
        return model_class.from_dict(
            self._handle_get_request(
                urljoin(self.redirect_map[model_class.redirect_key], str(id))
            )
        )

    def _handle_get_request(self, path, params=None):
        """send GET request to api and return json response

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
        return resp.json()

    def _handle_patch_request(self, path, data: dict):
        """send PATCH request to api

        Raises:
            requests.exceptions.RequestException
        """
        resp = requests.patch(
            path + "/",  # DRF requires trailing slash for patch method
            data=data,
            headers={"Authorization": self.token}
        )
        resp.raise_for_status()
