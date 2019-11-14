import requests
import urllib.parse
import typing
import json


class ZapisyApi:

    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url

    def get_semesters(self, visible=None):
        return map(Semester.from_json, self._handle_request(
            path="/api/v1/semesters/",
            params={"visible": visible}
        ))

    def _handle_request(self, path, params):
        resp = requests.get(
            urllib.parse.urljoin(self.base_url, path),
            headers={"Authorization": self.token},
            params=params
        )
        resp.raise_for_status()
        return resp.json()

class Model:
    @classmethod
    def from_json(cls, json):
        dict_ = json.loads(json)
        cls._from_dict(dict_)

    @classmethod
    def _from_dict(cls, dict_):
        return cls(**dict_)

    def _to_json(self):
        return json.dumps(self.__dict__)


class Semester(Model):
    def __init__(self,
                 id: int,
                 display_name: str,
                 year: str,
                 type: str):
        self.id = id
        self.display_name = display_name
        self.year = year
        self.type = type


