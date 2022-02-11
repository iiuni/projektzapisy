from django.test import TestCase

from apps.theses.enums import ThesisStatus, ThesisVote
from apps.theses.forms import EditThesisForm, ThesisForm
from apps.theses.models import ThesesSystemSettings, Thesis, Vote
from apps.users.tests.factories import EmployeeFactory, StudentFactory


class ThesisStatusChangeTestCase(TestCase):
    def setUp(self):
        self.thesis_owner = EmployeeFactory()

        Thesis.objects.create(title="thesis_vote_0",
                              advisor=self.thesis_owner,
                              kind=0,
                              status=ThesisStatus.BEING_EVALUATED,
                              max_number_of_students=1)
        thesis_vote_1 = Thesis.objects.create(title="thesis_vote_1",
                                              advisor=self.thesis_owner,
                                              kind=0,
                                              status=ThesisStatus.BEING_EVALUATED,
                                              max_number_of_students=1)
        thesis_vote_1.students.add(StudentFactory())

        Thesis.objects.create(title="thesis_edit_0",
                              advisor=self.thesis_owner,
                              kind=0,
                              status=ThesisStatus.ACCEPTED,
                              max_number_of_students=1)
        Thesis.objects.create(title="thesis_edit_1",
                              advisor=self.thesis_owner,
                              kind=0,
                              status=ThesisStatus.RETURNED_FOR_CORRECTIONS,
                              max_number_of_students=1)
        test_edit_2 = Thesis.objects.create(title="thesis_edit_2",
                                            advisor=self.thesis_owner,
                                            kind=0,
                                            status=ThesisStatus.IN_PROGRESS,
                                            max_number_of_students=1)
        test_edit_2.students.add(StudentFactory())

        ThesesSystemSettings.objects.create(num_required_votes=4)

    def test_vote(self):
        thesis_vote_0 = Thesis.objects.get(title="thesis_vote_0")
        thesis_vote_1 = Thesis.objects.get(title="thesis_vote_1")

        vote_0 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_0)
        vote_1 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_1)
        vote_2 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_0)
        vote_3 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_0)
        vote_4 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_0)
        vote_5 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_1)
        vote_6 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_1)
        vote_7 = Vote.objects.create(owner=EmployeeFactory(),
                                     vote=ThesisVote.ACCEPTED, thesis=thesis_vote_1)

        vote_0.save()
        vote_1.save()
        vote_2.save()
        vote_3.save()
        vote_4.save()
        vote_5.save()
        vote_6.save()
        vote_7.save()

        self.assertEqual(thesis_vote_0.status, ThesisStatus.ACCEPTED)
        self.assertEqual(thesis_vote_1.status, ThesisStatus.IN_PROGRESS)

    def test_edit(self):
        thesis_edit_0 = Thesis.objects.get(title="thesis_edit_0")
        thesis_edit_1 = Thesis.objects.get(title="thesis_edit_1")
        thesis_edit_2 = Thesis.objects.get(title="thesis_edit_2")

        form_data_0 = {'title': thesis_edit_0.title,
                       'advisor': thesis_edit_0.advisor_id, 'kind': 0,
                       'students': [StudentFactory()],
                       'max_number_of_students': 2}
        form_data_1 = {'title': thesis_edit_1.title,
                       'advisor': thesis_edit_1.advisor_id, 'kind': 0,
                       'max_number_of_students': 2}
        form_data_2 = {'title': thesis_edit_2.title,
                       'advisor': thesis_edit_2.advisor_id, 'kind': 0,
                       'max_number_of_students': 2}

        form_0 = EditThesisForm(instance=thesis_edit_0,
                                user=self.thesis_owner.user, data=form_data_0)
        form_1 = EditThesisForm(instance=thesis_edit_1,
                                user=self.thesis_owner.user, data=form_data_1)
        form_2 = EditThesisForm(instance=thesis_edit_2,
                                user=self.thesis_owner.user, data=form_data_2)

        form_0.save(commit=True)
        form_1.save(commit=True)
        form_2.save(commit=True)

        self.assertEqual(thesis_edit_0.status,
                         ThesisStatus.IN_PROGRESS.value)
        self.assertEqual(thesis_edit_1.status,
                         ThesisStatus.BEING_EVALUATED.value)
        self.assertEqual(thesis_edit_2.status,
                         ThesisStatus.ACCEPTED.value)

    def test_max_number_of_students_not_valid(self):
        form_data = {'title': 'Praca dyplomowa',
                     'advisor': self.thesis_owner, 'kind': 0,
                     'students': [StudentFactory(), StudentFactory(), StudentFactory()],
                     'max_number_of_students': 2}

        thesis_form = ThesisForm(user=self.thesis_owner.user, data=form_data)

        self.assertRaises(ValueError, thesis_form.save, commit=True)

    def test_max_number_of_students_valid(self):
        form_data = {'title': 'Praca dyplomowa',
                     'advisor': self.thesis_owner, 'kind': 0,
                     'students': [StudentFactory(), StudentFactory()],
                     'max_number_of_students': 2}

        thesis_form = ThesisForm(user=self.thesis_owner.user, data=form_data)

        thesis_form.save(commit=True)

        self.assertTrue(thesis_form.is_valid())
