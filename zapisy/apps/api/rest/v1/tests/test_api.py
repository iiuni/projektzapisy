from django.test import TestCase
from rest_framework.test import APIClient

from apps.offer.vote.models import SystemState, SingleVote
from apps.api.rest.v1.views import SingleVoteViewSet, SystemStateViewSet


class VoteSystemTests(TestCase):
    def setUp(self):
        state = SystemState(year=2010)
        state.save()
        state = SystemState(year=2018)
        state.save()

    """Get system states (there was none, so we get only states from setUp)
    Check if content is JSON and contains expected data"""
    def test_system_states_endpoint(self):
        client = APIClient()
        response = client.get('/api/v1/systemstate/')
        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(json.dumps(response.data))
        self.assertEqual(len(resp_json), 2)
        self.assertEqual(resp_json[0], {"id": 1, "state_name": "Ustawienia systemu na rok 2010"})
        self.assertEqual(resp_json[1], {"id": 2, "state_name": "Ustawienia systemu na rok 2018"})

    """Test votes endpoint, there are no votes in test database,
    only check if resource was found"""
    def test_votes_endpoint(self):
        client = APIClient()
        response = client.get('/api/v1/votes/', params=(('state', 1)))
        self.assertEqual(response.status_code, 200)
