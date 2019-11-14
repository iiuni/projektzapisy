import unittest
from unittest import mock
from sz_api import ZapisyApi


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            pass

    if args[0] == 'https://zapisy.ii.uni.wroc.pl/api/v1/semesters/':
        return MockResponse([
                          {
                              "id": 342,
                              "display_name": "2019/20 zimowy",
                              "year": "2019/20",
                              "type": "z",
                              "usos_kod": None
                          },
                          {
                              "id": 341,
                              "display_name": "2018/19 letni",
                              "year": "2018/19",
                              "type": "l",
                              "usos_kod": None
                          }], 200)
    return MockResponse(None, 404)


class TestSemester(unittest.TestCase):

    def setUp(self):
        self.api = ZapisyApi(token="Token test",
                             base_url="https://zapisy.ii.uni.wroc.pl")

    @mock.patch('sz_api.requests.get', side_effect=mocked_requests_get)
    def test_get_semesters(self, mock_get):
        resp = self.api.get_semesters()
        self.assertEquals({record["id"] for record in resp}, {342, 341})
