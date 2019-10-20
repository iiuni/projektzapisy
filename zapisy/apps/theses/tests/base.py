import random
from typing import Callable, List

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group

from apps.users.models import Employee, Student, BaseUser
from apps.users.tests.factories import EmployeeFactory, StudentFactory
from ..models import (
    Thesis, ThesisVote, ThesisStatus, VoteToProcess,
    ThesesSystemSettings
)

from ..users import THESIS_BOARD_GROUP_NAME

from .utils import (
    random_title, random_bool,
    random_kind, random_current_status, random_reserved_until,
    random_description, random_definite_vote,
)

PAGE_SIZE = 100


class ThesesBaseTestCase(APITestCase):
    """A test case base class for theses tests that takes care of user creation
    and provides common utilities
    """
    @classmethod
    def setUpTestData(cls):
        cls.create_users()

    NUM_BOARD_MEMBERS = 7

    @classmethod
    def create_users(cls):
        NUM_STUDENTS = 15
        NUM_EMPLOYEES = cls.NUM_BOARD_MEMBERS * 2
        StudentFactory.create_batch(NUM_STUDENTS)
        EmployeeFactory.create_batch(NUM_EMPLOYEES)
        cls.students = list(Student.objects.all())
        cls.employees = list(Employee.objects.all())
        cls.board_group = Group.objects.get(name=THESIS_BOARD_GROUP_NAME)

        cls.staff_user = Employee.objects.all()[0]
        cls.staff_user.user.is_staff = True
        cls.staff_user.user.save()

        cls.board_members = []
        for i in range(cls.NUM_BOARD_MEMBERS):
            member = Employee.objects.all()[i]
            cls.board_members.append(member)
            cls.board_group.user_set.add(member.user)

        cls.rejecter = random.choice(cls.board_members)
        settings = ThesesSystemSettings.objects.get()
        settings.master_rejecter = cls.rejecter
        settings.save()

    @classmethod
    def get_random_emp(cls):
        """Return a random employee (not an admin or a board member)"""
        return random.choice(cls.employees[1 + cls.NUM_BOARD_MEMBERS:])

    @classmethod
    def get_random_emp_different_from(cls, emp):
        """Return a random employee different from the specified employee"""
        result = cls.get_random_emp()
        while result == emp:
            result = cls.get_random_emp()
        return result

    @classmethod
    def get_admin(cls):
        return cls.staff_user

    @classmethod
    def get_random_board_member(cls):
        """Get a random member of the theses board, _possibly the admin_"""
        return random.choice(cls.board_members)

    @classmethod
    def get_random_board_member_other_than(cls, members: List[Employee]):
        """Return a random board member different from the specified one"""
        result = cls.get_random_board_member()
        while members and result in members:
            result = cls.get_random_board_member()
        return result

    @classmethod
    def get_random_board_member_not_admin(cls):
        """Get a random board member, but not the admin"""
        return cls.get_random_board_member_other_than([cls.get_admin()])

    @classmethod
    def get_random_board_member_not_rejecter(cls):
        return cls.get_random_board_member_other_than([cls.get_rejecter()])

    @classmethod
    def get_random_board_member_not_admin_or_rejecter(cls):
        return cls.get_random_board_member_other_than([
            cls.get_rejecter(), cls.get_admin(),
        ])

    @classmethod
    def get_rejecter(cls):
        return cls.rejecter

    @classmethod
    def get_random_student(cls):
        return random.choice(cls.students)

    @classmethod
    def get_random_students(cls, num_students: int) -> List[Student]:
        """Get the specified number of unique random students"""
        assert num_students < len(cls.students)
        result = []
        while len(result) < num_students:
            s = cls.get_random_student()
            while s in result:
                s = cls.get_random_student()
            result.append(s)
        return result

    @classmethod
    def make_thesis_nosave(cls, **kwargs):
        """Create a thesis instance using the provided params or defaults,
        without saving it (only creates an instance)
        Because students is a m2m relationship, no students will be assigned"""
        return Thesis(
            title=kwargs.get("title", random_title()),
            advisor=kwargs.get("advisor", cls.get_random_emp()),
            supporting_advisor=kwargs.get(
                "supporting_advisor", cls.get_random_emp() if random_bool() else None
            ),
            kind=kwargs.get("kind", random_kind()).value,
            status=kwargs.get("status", random_current_status()).value,
            reserved_until=kwargs.get("reserved_until", random_reserved_until()),
            description=kwargs.get("description", random_description()),
        )

    @classmethod
    def make_thesis(cls, **kwargs):
        """Like make_thesis, but also saves to the DB.
        This allows the method to assign students
        """
        if "students" in kwargs:
            students = kwargs.pop("students")
        else:
            students = cls.get_random_students(random.randint(1, 10))
        result = cls.make_thesis_nosave(**kwargs)
        result.save()
        result.set_students(students)
        return result

    def get_board_members(self, num: int, to_skip: Employee=None):
        def get_voter():
            if to_skip:
                return self.get_random_board_member_other_than([to_skip])
            return self.get_random_board_member()
        voters = []
        while len(voters) < num:
            voter = get_voter()
            while voter in voters:
                voter = get_voter()
            voters.append(voter)
        return voters

    def login_as(self, user: BaseUser):
        """Login as the specified user"""
        self.client.login(username=user.user.username, password="test")

    def get_response_with_data(self, data={}):
        """Make a request to the theses list endpoint with the specified params,
        return the raw response
        """
        url = reverse("theses:theses-list")
        if "limit" not in data:
            data["limit"] = PAGE_SIZE
        return self.client.get(url, data)

    def get_theses_with_data(self, data={}):
        """Download and return theses with the provided params"""
        response = self.get_response_with_data(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["results"]

    def create_theses_for_ungraded_testing(self, board_member: Employee):
        """
        Create two batches of theses, one graded, the other one not
        graded or graded with indeterminate vote values for the given
        board member"""
        num_theses = random.randint(10, 20)
        graded_theses = [self.make_thesis(status=ThesisStatus.BEING_EVALUATED) for _ in range(num_theses)]
        ungraded_theses = [self.make_thesis(status=ThesisStatus.BEING_EVALUATED) for _ in range(num_theses)]
        for graded in graded_theses:
            self.set_thesis_vote_locally(graded, board_member, random_definite_vote())
        # Also cast "indeterminate" votes for some "ungraded" theses,
        # they should still count as ungraded with those vote values
        ungraded_with_indeterminate = random.sample(ungraded_theses, random.randrange(num_theses))
        for thesis in ungraded_with_indeterminate:
            self.set_thesis_vote_locally(thesis, board_member, {"value": ThesisVote.NONE})
        # Pick a few theses, set them to one of the unchangeable statues;
        # they shouldn't count anymore
        unchangeable_theses = random.sample(ungraded_theses, random.randrange(num_theses // 3))
        # only "being evaluated" is counted as ungraded
        uncounted_statuses = list(set(list(ThesisStatus)) - set((ThesisStatus.BEING_EVALUATED, )))
        for unchangeable in unchangeable_theses:
            unchangeable.status = random.choice(uncounted_statuses).value
            unchangeable.save()
        # They shouldn't be counted as ungraded anymore
        ungraded_theses = list(set(ungraded_theses) - set(unchangeable_theses))
        return graded_theses, ungraded_theses

    def set_thesis_vote_locally(self, thesis: Thesis, voter: Employee, vote: ThesisVote):
        """Set the specified vote value for the specified employee locally,
        not through the API
        """
        vote_to_process = VoteToProcess(voter, vote["value"], vote.get("reason"))
        thesis.process_new_votes((vote_to_process, ), voter, True)

    def run_test_with_privileged_users(
        self, test_func: Callable[[Employee], None],
    ):
        """Run the provided testing function with all privileged user types,
        that is an employee, a non admin board member, and the admin
        """
        test_func(self.get_random_emp())
        self.run_test_with_board_members(test_func)

    def run_test_with_board_members(
        self, test_func: Callable[[Employee], None],
    ):
        """Run the provided testing function with a non admin board member
        and the admin
        """
        admin = self.get_admin()
        test_func(self.get_random_board_member_not_admin())
        test_func(admin)
