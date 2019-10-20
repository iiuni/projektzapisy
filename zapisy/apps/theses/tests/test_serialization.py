import random

from apps.users.models import BaseUser

from ..models import ThesisStatus
from .base import ThesesBaseTestCase
from .utils import random_definite_vote, exactly_one


class ThesesSerializationTestCase(ThesesBaseTestCase):
    """Basic tests to ensure thesis serialization works correctly"""
    def setUp(self):
        self.advisor = self.get_random_emp()
        self.thesis = self.make_thesis(advisor=self.advisor, status=ThesisStatus.ACCEPTED)

    def get_serialized_thesis(self):
        return self.get_theses_with_data()[0]

    def test_basic_fields_serialized_correctly(self):
        self.login_as(self.get_random_emp())
        thesis = self.get_serialized_thesis()
        self.assertEqual(thesis["title"], self.thesis.title)
        self.assertEqual(thesis["advisor"], self.advisor.pk)
        self.assertEqual(
            thesis["supporting_advisor"],
            self.thesis.supporting_advisor.pk if self.thesis.supporting_advisor else None
        )
        self.assertEqual(thesis["kind"], self.thesis.kind)
        self.assertEqual(thesis["status"], self.thesis.status)
        self.assertEqual(
            thesis["reserved_until"],
            str(self.thesis.reserved_until) if self.thesis.reserved_until else None
        )
        self.assertEqual(thesis["description"], self.thesis.description)
        num_serialized_students = len(thesis["students"])
        self.assertEqual(num_serialized_students, self.thesis.students.count())
        for student in self.thesis.get_students():
            self.assertTrue(
                exactly_one(
                    recv_student["id"] == student.pk
                    for recv_student in thesis["students"]
                )
            )

    def _get_thesis_with_votes(self, user: BaseUser):
        board_members = self.get_board_members(random.randint(2, 5))
        temp_board_member = self.get_random_emp()
        # Also add a vote by a previous board member to check that too
        self.board_group.user_set.add(temp_board_member.user)
        votes = [(member, random_definite_vote()) for member in board_members]
        votes.append((temp_board_member, random_definite_vote()))
        self.board_group.user_set.remove(temp_board_member.user)
        for voter, vote in votes:
            self.set_thesis_vote_locally(self.thesis, voter, vote)
        self.login_as(user)
        thesis = self.get_serialized_thesis()
        return thesis, votes

    def _test_no_votes_for(self, user: BaseUser):
        thesis, _ = self._get_thesis_with_votes(user)
        self.assertNotIn("votes", thesis)

    def test_vote_counts_for_student(self):
        self._test_no_votes_for(self.get_random_student())

    def test_vote_counts_for_emp(self):
        self._test_no_votes_for(self.get_random_emp())

    def _test_vote_details_for(self, user: BaseUser):
        thesis, votes = self._get_thesis_with_votes(user)
        self.assertIn("votes", thesis)
        votes_dict = thesis["votes"]
        self.assertEqual(len(set(votes_dict.keys())), len(votes))
        for voter_id, vote_details in votes_dict.items():
            vote_value = vote_details["value"]
            self.assertTrue(
                exactly_one((m.pk == voter_id and v["value"].value == vote_value for m, v in votes))
            )

    def test_vote_details_for_board_member(self):
        self._test_vote_details_for(self.get_random_board_member_not_admin())

    def test_vote_details_for_admin(self):
        self._test_vote_details_for(self.get_admin())
