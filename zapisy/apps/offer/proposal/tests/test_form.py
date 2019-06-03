import datetime

from django import test
import freezegun

from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.tests.factories import SemesterFactory
from apps.offer.proposal.forms import EditProposalForm
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.users.tests.factories import EmployeeFactory


class ProposalFormTest(test.TestCase):
    """Tests the proposal form."""

    @classmethod
    def setUpTestData(cls):
        cls.employee = EmployeeFactory()

        # We need to have one course type in database.
        cls.course_type = CourseType.objects.create(
            name="I2.Z - zastosowania inf.",
            short_name="I2.Z",
            default_ects=6,
        )

        # This form data will be used across tests.
        cls.form_data = {
            'name': "Szydełkowanie",
            'language': 'pl',
            'semester': 'u',
            'course_type': cls.course_type.pk,
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
        cls.semester = SemesterFactory()

    def test_current_course_modified(self):
        """Tests that the form also updates the current instance of the course.
        """
        # First, create the proposal.
        form = EditProposalForm(data=self.form_data, user=self.employee.user)
        form.save()
        proposal = Proposal.objects.get()

        # Create its course instance.
        course = CourseInstance.create_proposal_instance(proposal, self.semester)

        # Prepare the form input.
        form_data = self.form_data.copy()
        form_data.update({
            'description': "To jest bardzo trudny przedmiot",
        })
        with freezegun.freeze_time(self.semester.semester_beginning + datetime.timedelta(days=1)):
            # We edit the proposal during the semester and expect the course to
            # be updated.
            form = EditProposalForm(instance=proposal, data=form_data, user=self.employee.user)
            self.assertTrue(form.is_valid())
            form.save()
            course.refresh_from_db()
            self.assertEqual(course.description, "To jest bardzo trudny przedmiot")

    def test_past_course_intact(self):
        """Tests that the form does not update past course instances."""
        # First, create the proposal.
        form = EditProposalForm(data=self.form_data, user=self.employee.user)
        form.save()
        proposal = Proposal.objects.get()

        # Create its course instance.
        course = CourseInstance.create_proposal_instance(proposal, self.semester)

        # Prepare the form input.
        form_data = self.form_data.copy()
        form_data.update({
            'description': "To jest bardzo trudny przedmiot",
        })
        with freezegun.freeze_time(self.semester.semester_ending + datetime.timedelta(days=1)):
            # We edit the proposal during the semester and expect the course to
            # be updated.
            form = EditProposalForm(instance=proposal, data=form_data, user=self.employee.user)
            self.assertTrue(form.is_valid())
            form.save()
            proposal.refresh_from_db()
            course.refresh_from_db()
            self.assertEqual(proposal.description, "To jest bardzo trudny przedmiot")
            self.assertNotEqual(course.description, "To jest bardzo trudny przedmiot")
