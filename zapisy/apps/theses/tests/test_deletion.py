from rest_framework import status
from django.urls import reverse

from apps.users.models import Employee, BaseUser
from ..models import ThesisStatus
from ..permissions import EMPLOYEE_DELETABLE_STATUSES
from ..enums import NOT_READY_STATUSES
from .base import ThesesBaseTestCase


class ThesesDeletionTestCase(ThesesBaseTestCase):
    def setUp(self):
        self.advisor = self.get_random_emp()
        self.thesis = self.make_thesis(advisor=self.advisor, status=ThesisStatus.BEING_EVALUATED)

    def delete_thesis(self, deleter: Employee, **kwargs):
        """Try to delete the current thesis as the specified user
        """
        self.login_as(deleter)
        return self.client.delete(f'{reverse("theses:theses-list")}{self.thesis.pk}/')

    def _test_cannot_delete(self, person: BaseUser):
        response = self.delete_thesis(person)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_can_delete(self, person: BaseUser):
        response = self.delete_thesis(person)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def _set_status(self, thesis_status: ThesisStatus):
        self.thesis.status = thesis_status.value
        self.thesis.save()

    def _test_can_delete_with_status(self, person: Employee, thesis_status: ThesisStatus):
        self._set_status(thesis_status)
        self._test_can_delete(person)

    def _test_cannot_delete_with_status(self, person: Employee, thesis_status: ThesisStatus):
        self._set_status(thesis_status)
        self._test_cannot_delete(person)

    def test_student_cannot_delete_not_ready_thesis(self):
        """Test that students cannot delete theses that are not ready yet
        they should get a 404 since those aren't even visible to them
        """
        stud = self.get_random_student()
        for thesis_status in NOT_READY_STATUSES:
            self._set_status(thesis_status)
            response = self.delete_thesis(stud)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_delete_ready_thesis(self):
        """Test that students get a 403 when they try to delete a thesis
        that should be visible to them
        """
        stud = self.get_random_student()
        for thesis_status in list(set(ThesisStatus) - set(NOT_READY_STATUSES)):
            self._test_cannot_delete_with_status(stud, thesis_status)

    def test_employee_can_delete_own_thesis_when_being_evaluated(self):
        """Test that employees are allowed to delete their own thesis if it's still being evaluated"""
        self._test_can_delete_with_status(self.advisor, ThesisStatus.BEING_EVALUATED)

    def test_employee_can_delete_own_thesis_when_rejected(self):
        """Test that employees are allowed to delete their own thesis if it's been returned for corrections"""
        self._test_can_delete_with_status(self.advisor, ThesisStatus.RETURNED_FOR_CORRECTIONS)

    def test_employee_cannot_delete_own_thesis_after_accepted(self):
        """Test that employees cannot delete their own thesis after it's been accepted"""
        post_accept = list(set(ThesisStatus) - set(EMPLOYEE_DELETABLE_STATUSES))
        for thesis_status in post_accept:
            self._test_cannot_delete_with_status(self.advisor, thesis_status)

    def test_employee_cannot_delete_someone_elses_thesis(self):
        """Test that employees are not allowed to delete someone else's theses"""
        other_emp = self.get_random_emp_different_from(self.advisor)
        self._test_cannot_delete(other_emp)

    def test_board_member_can_delete_someone_elses_thesis(self):
        """Test that board members are allowed to delete someone else's theses"""
        member = self.get_random_board_member_not_admin()
        self._test_can_delete(member)

    def test_board_member_can_delete_accepted_thesis(self):
        member = self.get_random_board_member_not_admin()
        self._test_can_delete_with_status(member, ThesisStatus.ACCEPTED)

    def test_board_member_cannot_delete_archived_thesis(self):
        """Board members are not allowed to modify or delete archived theses"""
        member = self.get_random_board_member_not_admin()
        self._test_cannot_delete_with_status(member, ThesisStatus.DEFENDED)

    def test_admin_can_delete_someone_elses_thesis(self):
        self._test_can_delete(self.get_admin())

    def test_admin_can_delete_accepted_thesis(self):
        self._test_can_delete_with_status(self.get_admin(), ThesisStatus.ACCEPTED)

    def test_admin_cannot_delete_archived_thesis(self):
        """Admins are allowed to delete even archived theses"""
        self._test_can_delete_with_status(self.get_admin(), ThesisStatus.DEFENDED)
