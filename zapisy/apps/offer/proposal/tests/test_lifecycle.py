from django import test

from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.models.points import PointTypes
from apps.offer.proposal.forms import EditProposalForm
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.users.tests.factories import EmployeeFactory


class LifecycleTest(test.TestCase):
    """Tests that the proposal form does not allow an employee to walk around
    the lifecycle of a course proposal.
    """

    @classmethod
    def setUpTestData(cls):
        cls.employee = EmployeeFactory()

        # We need to have one course type in database.
        cls.course_type = CourseType.objects.create(
            name="I2.Z - zastosowania inf.",
            short_name="I2.Z",
            default_ects=6,
        )

        # This will go away with entire PointTypes model.
        PointTypes.objects.create(id=1, name='ECTS')

    def test_employee_can_create_draft(self):
        """Tests that the employee can create an (almost empty) draft proposal.
        """
        form_data = {
            'name': "Szydełkowanie",
            'language': 'pl',
            'semester': 'u',
            'course_type': self.course_type.pk,
            'has_exam': True,
            'recommended_for_first_year': True,
            'hours_lecture': 30,
            'hours_exercise': 30,
            'hours_lab': 0,
            'hours_exercise_lab': 0,
            'hours_seminar': 0,
            'hours_recap': 15,
            'status': ProposalStatus.DRAFT,
        }
        form = EditProposalForm(data=form_data, user=self.employee.user)
        self.assertTrue(form.is_valid())
        form.save()
        p = Proposal.objects.get(name="Szydełkowanie")
        self.assertEqual(p.status, ProposalStatus.DRAFT)

    def test_employee_cannot_put_proposal_into_offer(self):
        """Tests that the employee cannot put the proposal directly into offer.
        """
        form_data = {
            'name': "Szydełkowanie",
            'language': 'pl',
            'semester': 'u',
            'course_type': self.course_type.pk,
            'has_exam': True,
            'recommended_for_first_year': True,
            'hours_lecture': 30,
            'hours_exercise': 30,
            'hours_lab': 0,
            'hours_exercise_lab': 0,
            'hours_seminar': 0,
            'hours_recap': 15,
            'status': ProposalStatus.IN_OFFER,
        }
        form = EditProposalForm(data=form_data, user=self.employee.user)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_employee_can_fix_proposal(self):
        """The proposal has been marked as CORRECTIONS_REQUIRED by the head of
        teaching. The employee needs to correct it now."""
        # First employee creates a proposal.
        form_data = {
            'name': "Szydełkowanie",
            'language': 'pl',
            'semester': 'u',
            'course_type': self.course_type.pk,
            'has_exam': True,
            'recommended_for_first_year': True,
            'hours_lecture': 30,
            'hours_exercise': 30,
            'hours_lab': 0,
            'hours_exercise_lab': 0,
            'hours_seminar': 0,
            'hours_recap': 15,
            'objectives': ("Celami przedmiotu jest zapoznanie studentów z technikami "
                           "szydełkowania oraz nauczenie ich cierpliwości niezbędnej "
                           "do wykonywania tej czynności."),
            'contents': ("1. Różnice między szydełkowaniem i robieniem na drutach.\n"
                         "2. Podstawowe wzory szydełkowe."),
            'literature': "* Wildman, Emily. _Step-By-Step Crochet_, 1972\n",
            'status': ProposalStatus.PROPOSAL,
        }
        form = EditProposalForm(data=form_data, user=self.employee.user)
        form.save()

        # Second, its status is changed to CORRECTIONS_REQUIRED
        proposal = Proposal.objects.get(name="Szydełkowanie")
        proposal.status = ProposalStatus.CORRECTIONS_REQUIRED
        proposal.save()

        # Third, the employee makes amends.
        form_data.update({
            'hours_exercise': 0,
            'hours_lab': 30,
            'status': ProposalStatus.PROPOSAL,
        })
        form = EditProposalForm(instance=proposal, data=form_data, user=self.employee.user)
        self.assertTrue(form.is_valid())

        # However, he may not put it in the offer.
        proposal.refresh_from_db()
        form_data.update({
            'status': ProposalStatus.IN_OFFER,
        })
        form = EditProposalForm(instance=proposal, data=form_data, user=self.employee.user)
        self.assertFalse(form.is_valid())

        # Nor can he put it under vote.
        proposal.refresh_from_db()
        form_data.update({
            'status': ProposalStatus.IN_VOTE,
        })
        form = EditProposalForm(instance=proposal, data=form_data, user=self.employee.user)
        self.assertFalse(form.is_valid())
