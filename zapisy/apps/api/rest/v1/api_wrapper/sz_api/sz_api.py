import requests
from typing import Iterator
import urllib.parse
from pprint import pprint

from .models import (Semester, User, Student)


class ZapisyApi:

    def __init__(self, token: str, api_url: str):
        self.token = token
        self.redirect_map = self._get_redirect_map("http://testserver/api/v1/semesters/")

    def _get_redirect_map(self, api_url: str) -> dict:
        return self._handle_request(api_url)

    def _get_semesters(self) -> Iterator[Semester]:
        """
        Gets an iterator over Semester objects
        """
        return self._get_deserialized_data(Semester)

    def get_students(self) -> Iterator[Student]:
        """
        Gets an iterator over Student objects
        """
        return self._get_deserialised_data(Student)

    def _get_deserialized_data(self, model_class, params=None):
        if model_class.is_paginated:
            data_gen = self._get_paginated_data(model_class, params)
        else:
            data_gen = self._get_unpaginated_data(model_class, params)
        yield from map(model_class.from_dict, data_gen)

    def _get_paginated_data(self, model_class, params=None):
        response = self._handle_request(
            self.redirect_map[model_class.redirect_key], params)
        yield from iter(response["results"])

        while response["next"] is not None:
            response = self._handle_request(response["next"], params)
            yield from iter(response["results"])

    def _get_unpaginated_data(self, model_class, params=None):
        yield from iter(self._handle_request(
            self.redirect_map[model_class.redirect_key], params))

    def _handle_request(self, path, params=None):
        resp = requests.get(
            path,
            headers={"Authorization": self.token},
            params=params
        )
        resp.raise_for_status()
        return resp.json()
