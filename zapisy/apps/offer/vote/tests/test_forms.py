from datetime import date

from django import test
from django.contrib.contenttypes.models import ContentType
from freezegun import freeze_time

from apps.enrollment.courses.tests.factories import CourseInstanceFactory, SemesterFactory
from apps.offer.proposal.tests.factories import ProposalFactory
from apps.offer.vote.models import SingleVote, SystemState
from apps.users.tests.factories import StudentFactory
from apps.offer.proposal.models import ProposalStatus, SemesterChoices

from ..forms import prepare_vote_formset


class VoteFormsetTest(test.TestCase):
    """Tests for the vote formset.

    In our test scenario there will be one system state and six proposals in
    vote — four in winter semester, one in summer and one undecided. One of the
    proposals in winter semester is going to be free to vote for.

    The overall point limit for voting in our test is reduced to 10.
    """

    @classmethod
    def setUpTestData(cls):
        # Student 1 will be voting. Student 2 will be taking part in a
        # correction (his primary vote will already have been saved).
        cls.student1 = StudentFactory()
        cls.student2 = StudentFactory()
        cls.state = SystemState.objects.create(
            year="2011/12",
            semester_winter=SemesterFactory(year="2011/12", type=SemesterChoices.WINTER),
            semester_summer=SemesterFactory(year="2011/12", type=SemesterChoices.SUMMER),
            vote_beg=date(2011, 6, 1),
            vote_end=date(2011, 6, 14),
            winter_correction_beg=date(2011, 9, 7),
            winter_correction_end=date(2011, 9, 13),
            summer_correction_beg=date(2012, 1, 28),
            summer_correction_end=date(2012, 2, 1),
        )

        cls.proposals = [
            ProposalFactory(semester=SemesterChoices.WINTER, status=ProposalStatus.IN_VOTE),
            ProposalFactory(semester=SemesterChoices.WINTER, status=ProposalStatus.IN_VOTE),
            ProposalFactory(semester=SemesterChoices.WINTER, status=ProposalStatus.IN_VOTE),
            ProposalFactory(semester=SemesterChoices.WINTER, status=ProposalStatus.IN_VOTE),
            ProposalFactory(semester=SemesterChoices.SUMMER, status=ProposalStatus.IN_VOTE),
            ProposalFactory(semester=SemesterChoices.SUMMER, status=ProposalStatus.IN_OFFER),
            ProposalFactory(semester=SemesterChoices.UNASSIGNED, status=ProposalStatus.IN_VOTE),
        ]

        # One of the winter proposals is going to be free to vote for (point
        # limit will not apply to it).
        cls.proposals[2].course_type.free_in_vote = True
        cls.proposals[2].course_type.save()

        # We reduce the point limit to 10.
        SystemState.DEFAULT_MAX_POINTS = 10

        # We already save some votes for student2, so he will be ready for
        # correction.
        SingleVote.objects.bulk_create([
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[0], value=3),
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[1], value=0),
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[2], value=2),
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[3], value=2),
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[4], value=3),
            SingleVote(state=cls.state, student=cls.student2, proposal=cls.proposals[6], value=2),
        ])

        # Some of the courses will be opened in the winter semester.
        CourseInstanceFactory(semester=cls.state.semester_winter, offer=cls.proposals[0])
        CourseInstanceFactory(semester=cls.state.semester_winter, offer=cls.proposals[1])

    @freeze_time(date(2011, 5, 15))
    def test_no_form_when_voting_closed(self):
        self.assertRaises(AssertionError, prepare_vote_formset, self.state, self.student1)

    @freeze_time(date(2011, 6, 2))
    def test_vote_form_correct(self):
        formset = prepare_vote_formset(self.state, self.student1)
        # We expect that all IN_VOTE proposals are rendered in the formset.
        form_ids = [f.instance.proposal_id for f in formset]
        proposal_ids = [p.id for p in self.proposals if p.status == ProposalStatus.IN_VOTE]
        self.assertListEqual(form_ids, proposal_ids)

    def formset_data(self, formset, field, *points):
        """A helper function preparing form data.

        It is important that point are given in the same order as the proposals
        are laid out in the formset. Field should be either 'value' (when we are
        posting vote formset) or 'correction'.
        """
        if field not in ['value', 'correction']:
            raise AssertionError("'field' must be either 'value' or 'correction'.")
        data = {
            'form-TOTAL_FORMS': len(points),
            'form-INITIAL_FORMS': len(points),
            'form-MAX_NUM_FORMS': '',
        }
        for idx, val in enumerate(points):
            singlevote_id = formset[idx].instance.pk
            data.update({
                f'form-{idx}-id': singlevote_id,
                f'form-{idx}-{field}': val,
            })
        return data

    @freeze_time(date(2011, 6, 2))
    def test_cannot_exceed_limit(self):
        # The third value is not counted into the limit. The rest sum up to 11.
        formset = prepare_vote_formset(self.state, self.student1)
        data = self.formset_data(formset, 'value', 3, 1, 2, 2, 3, 2)
        formset = prepare_vote_formset(self.state, self.student1, data)
        self.assertFalse(formset.is_valid())

    @freeze_time(date(2011, 6, 2))
    def test_form_saves_votes(self):
        formset = prepare_vote_formset(self.state, self.student1)
        # The third value is not counted into the limit. The rest sum up to 10.
        # These votes values are the same student2 has given out.
        data = self.formset_data(formset, 'value', 3, 0, 2, 2, 3, 2)
        formset = prepare_vote_formset(self.state, self.student1, data)
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertQuerysetEqual(SingleVote.objects.filter(state=self.state, student=self.student1),
                                 [3, 0, 2, 2, 3, 2],
                                 transform=lambda sv: sv.value)

    @freeze_time(date(2011, 6, 2))
    def test_form_view(self):
        c = test.Client()
        c.force_login(self.student1.user)

        # Ensure no queries are skipped due to cached content type for Group.
        ContentType.objects.clear_cache()

        # This number is a bit artificial — we just care that it is a constant.
        # I have inspected the queries and they look ok, so this is just
        # supposed to test that no one breaks performance in the future.
        with self.assertNumQueries(14):
            response = c.get('/vote/vote/')
        self.assertContains(response, '<select', count=6)

        # Ensure no queries are skipped due to cached content type for Group.
        ContentType.objects.clear_cache()

        # Number of queries should not change when we add one more proposal.
        ProposalFactory(status=ProposalStatus.IN_VOTE)
        with self.assertNumQueries(14):
            response = c.get('/vote/vote/')
        self.assertContains(response, '<select', count=7)

    @freeze_time(date(2011, 9, 10))
    def test_correction_form_correct(self):
        formset = prepare_vote_formset(self.state, self.student2)
        formset_ids = [f.instance.proposal_id for f in formset]
        courses_in_winter_proposal_ids = [self.proposals[0].id, self.proposals[1].id]
        self.assertListEqual(formset_ids, courses_in_winter_proposal_ids)

    @freeze_time(date(2011, 9, 10))
    def test_cannot_exceed_limit_in_correction(self):
        # Student2 spent 3 + 0 + 2 = 5 points in his primary vote on (not-free)
        # winter proposals. He must not be allowed to spend 6 points in winter
        # correction.
        formset = prepare_vote_formset(self.state, self.student2)
        data = self.formset_data(formset, 'correction', 3, 3)
        formset = prepare_vote_formset(self.state, self.student2, data)
        self.assertFalse(formset.is_valid())

    @freeze_time(date(2011, 9, 10))
    def test_cannot_lower_vote_value_in_correction(self):
        formset = prepare_vote_formset(self.state, self.student2)
        data = self.formset_data(formset, 'correction', 2, 3)
        formset = prepare_vote_formset(self.state, self.student2, data)
        self.assertFalse(formset.is_valid())

    @freeze_time(date(2011, 9, 10))
    def test_form_saves_correction(self):
        formset = prepare_vote_formset(self.state, self.student2)
        data = self.formset_data(formset, 'correction', 3, 2)
        formset = prepare_vote_formset(self.state, self.student2, data)
        self.assertTrue(formset.is_valid())
        formset.save()

        votes_in_semester = SingleVote.objects.filter(
            state=self.state, student=self.student2).in_semester(self.state.semester_winter)
        self.assertQuerysetEqual(votes_in_semester, [3, 2], transform=lambda sv: sv.val)
