import random

from apps.users.models import Employee

from ..models import Thesis, ThesisStatus, ThesisKind
from ..views import ThesisTypeFilter
from .base import ThesesBaseTestCase, PAGE_SIZE
from .utils import (
    random_current_status, random_available_status,
    random_status, make_employee_with_name, exactly_one,
    random_reserved_until
)


class ThesesFiltersAndSortingTestCase(ThesesBaseTestCase):
    """Tests the the filtering & sorting functionality works correctly"""
    def login_for_perms(self):
        """A simple helper that logs in as any user authorized to view theses
        so that we can test filters"""
        self.login_as(self.get_random_emp())

    def test_title_filter(self):
        num_matching = random.randint(1, PAGE_SIZE // 2)
        num_nonmatching = random.randint(1, PAGE_SIZE // 2)
        title_base_match = "foobar"
        title_base_nonmatch = "{}blahblah"
        theses_matching = [
            self.make_thesis_nosave(title=f'{title_base_match}_{i}') for i in range(num_matching)
        ]
        theses_nonmatching = [
            self.make_thesis_nosave(title=title_base_nonmatch.format(i)) for i in range(num_nonmatching)
        ]
        Thesis.objects.bulk_create(theses_matching + theses_nonmatching)
        self.login_for_perms()
        theses = self.get_theses_with_data({"title": title_base_match})
        self.assertEqual(len(theses), num_matching)
        for thesis in theses:
            self.assertTrue(title_base_match in thesis["title"])

    def test_advisor_filter(self):
        num_matching = random.randint(1, PAGE_SIZE // 2)
        num_nonmatching = random.randint(1, PAGE_SIZE // 2)
        matching_emp = self.get_random_emp()
        nonmatching_emp = self.get_random_emp_different_from(matching_emp)
        theses_matching = [
            self.make_thesis_nosave(advisor=matching_emp) for i in range(num_matching)
        ]
        theses_nonmatching = [
            self.make_thesis_nosave(advisor=nonmatching_emp) for i in range(num_nonmatching)
        ]
        Thesis.objects.bulk_create(theses_matching + theses_nonmatching)
        self.login_for_perms()
        theses = self.get_theses_with_data({"advisor": matching_emp.get_full_name()})
        self.assertEqual(len(theses), num_matching)
        for thesis in theses:
            thesis_advisor = Employee.objects.get(pk=thesis["advisor"])
            self.assertTrue(thesis_advisor == matching_emp)

    def test_current_type_filter(self):
        """Test that current, i.e. not yet defended theses are being filtered correctly"""
        num_normal = random.randint(1, PAGE_SIZE // 2)
        num_defended = random.randint(1, PAGE_SIZE // 2)
        normal = [
            self.make_thesis_nosave(status=random_current_status()) for i in range(num_normal)
        ]
        defended = [
            self.make_thesis_nosave(status=ThesisStatus.DEFENDED) for i in range(num_defended)
        ]
        Thesis.objects.bulk_create(normal + defended)
        self.login_for_perms()
        theses = self.get_theses_with_data({"type": ThesisTypeFilter.CURRENT.value})
        self.assertEqual(len(theses), num_normal)
        for thesis in theses:
            self.assertNotEqual(thesis["status"], ThesisStatus.DEFENDED.value)

    def test_available_filter(self):
        """Test that the "available of type" filter works correctly"""
        num_matching_avail = random.randint(1, PAGE_SIZE // 3)
        num_matching_unavail = random.randint(1, PAGE_SIZE // 3)
        num_other = random.randint(1, PAGE_SIZE // 3)
        matching_avail = [
            self.make_thesis_nosave(
                kind=ThesisKind.BACHELORS,
                status=random_available_status(),
                reserved_until=None,
            ) for i in range(num_matching_avail)
        ]
        matching_unavail = [
            self.make_thesis_nosave(
                kind=ThesisKind.BACHELORS,
                status=random_status() if i % 2 else ThesisStatus.IN_PROGRESS,
                reserved_until=random_reserved_until() if bool(i % 2) else None
            ) for i in range(num_matching_unavail)
        ]
        other = [
            self.make_thesis_nosave(kind=ThesisKind.ISIM) for i in range(num_other)
        ]
        Thesis.objects.bulk_create(matching_avail + matching_unavail + other)
        self.login_for_perms()
        theses = self.get_theses_with_data({"type": ThesisTypeFilter.AVAILABLE_BACHELORS.value})
        self.assertEqual(len(theses), num_matching_avail)
        for thesis in theses:
            self.assertEqual(thesis["kind"], ThesisKind.BACHELORS.value)
            self.assertNotEqual(thesis["status"], ThesisStatus.IN_PROGRESS.value)
            self.assertNotEqual(thesis["status"], ThesisStatus.DEFENDED.value)
            self.assertIsNone(thesis["reserved_until"])

    def test_ungraded_filter(self):
        board_member = self.get_random_board_member()
        _, ungraded_theses = self.create_theses_for_ungraded_testing(board_member)
        self.login_as(board_member)
        theses = self.get_theses_with_data({"type": ThesisTypeFilter.UNGRADED.value})
        self.assertEqual(len(ungraded_theses), len(theses))
        for graded in ungraded_theses:
            self.assertTrue(exactly_one(recv_thesis["id"] == graded.pk for recv_thesis in theses))

    def test_title_sort(self):
        """Test that sorting by title works correctly"""
        current_titles = ["abc", "abd", "def", "zzz"]
        archived_titles = ["aaaa", "zyd"]
        currents = [
            self.make_thesis_nosave(title=cur_title, status=random_current_status())
            for cur_title in current_titles
        ]
        archiveds = [
            self.make_thesis_nosave(title=arch_title, status=ThesisStatus.DEFENDED)
            for arch_title in archived_titles
        ]
        all_theses = currents + archiveds
        Thesis.objects.bulk_create(random.sample(all_theses, len(all_theses)))
        self.login_for_perms()
        theses = self.get_theses_with_data({"column": "title", "dir": "asc"})
        self.assertEqual(len(theses), len(all_theses))
        all_titles = current_titles + archived_titles
        for i in range(len(all_theses)):
            self.assertEqual(theses[i]["title"], all_titles[i])

    def test_advisor_sort(self):
        """Test that sorting by advisor name works correctly"""
        current_adv_names = ["abc", "abd", "def", "zzz"]
        archived_adv_names = ["aaaa", "zyd"]
        currents = [
            self.make_thesis_nosave(
                advisor=make_employee_with_name(cur_adv_name),
                status=random_current_status()
            ) for cur_adv_name in current_adv_names
        ]
        archiveds = [
            self.make_thesis_nosave(
                advisor=make_employee_with_name(arch_adv_name),
                status=ThesisStatus.DEFENDED
            ) for arch_adv_name in archived_adv_names
        ]
        all_theses = currents + archiveds
        Thesis.objects.bulk_create(random.sample(all_theses, len(all_theses)))
        self.login_for_perms()
        theses = self.get_theses_with_data({"column": "advisor", "dir": "asc"})
        self.assertEqual(len(theses), len(all_theses))
        for i in range(len(all_theses)):
            thesis_advisor = Employee.objects.get(pk=theses[i]["advisor"])
            self.assertEqual(thesis_advisor, all_theses[i].advisor)
