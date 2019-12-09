import requests
from typing import Iterator, Optional

from .models import (Semester, Student)


class ZapisyApi:

    def __init__(self, token: str, api_url: str):
        self.token = token
        self.redirect_map = self._get_redirect_map(api_url)

    def _get_redirect_map(self, api_url: str) -> dict:
        return self._handle_request(api_url)

    def get_semesters(self,
                      visible: Optional[bool] = None) -> Iterator[Semester]:
        """
        Gets an iterator over Semester objects.

        if visible parameter is provided, filters results by its value
        """
        return self._get_deserialized_data(Semester, {"visible": visible})

    def get_students(self) -> Iterator[Student]:
        """
        Gets an iterator over Student objects
        """
        return self._get_deserialized_data(Student)

    def _get_deserialized_data(self, model_class, params=None):
        if model_class.is_paginated:
            data_gen = self._get_paginated_data(model_class, params)
        else:
            data_gen = self._get_unpaginated_data(model_class, params)
        yield from map(model_class.from_dict, data_gen)

    def _get_paginated_data(self, model_class, params):
        response = self._handle_request(
            self.redirect_map[model_class.redirect_key], params)
        yield from iter(response["results"])

        while response["next"] is not None:
            response = self._handle_request(response["next"], params)
            yield from iter(response["results"])

    def _get_unpaginated_data(self, model_class, params):
        yield from iter(self._handle_request(
            self.redirect_map[model_class.redirect_key], params))

    def _handle_request(self, path, params=None):
        params = dict() if params is None else params

        resp = requests.get(
            path,
            headers={"Authorization": self.token},
            # filter out None params
            params={k: v for k, v in params.items() if v is not None}
        )
        resp.raise_for_status()
        return resp.json()
