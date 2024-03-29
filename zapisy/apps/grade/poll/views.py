import itertools
import json
from collections import defaultdict
from operator import attrgetter
from typing import List

from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.views.generic import TemplateView, UpdateView, View

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.forms import SubmissionEntryForm, TicketsEntryForm
from apps.grade.poll.models import Poll, Submission
from apps.grade.poll.utils import (PollSummarizedResults, SubmissionStats, check_grade_status,
                                   group)
from apps.grade.ticket_create.models.rsa_keys import RSAKeys


class TicketsEntry(TemplateView):
    template_name = 'poll/tickets_enter.html'

    def get(self, request):
        """Displays a basic but sufficient form for entering tickets."""
        form = TicketsEntryForm()
        is_grade_active = check_grade_status()

        return render(
            request,
            self.template_name,
            {
                'form': form,
                'is_grade_active': is_grade_active,
            },
        )

    def post(self, request):
        """Accepts and checks whether given tickets can be decoded.

        If the parsing via tickets_create's `SigningKey` module succeeds,
        redirects the user to the SubmissionEntry view.
        """
        form = TicketsEntryForm(request.POST)

        if form.is_valid():
            tickets = form.cleaned_data['tickets']
            try:
                correct_polls, failed_polls = RSAKeys.parse_raw_tickets(tickets)
            except json.JSONDecodeError:
                messages.error(
                    request, "Wprowadzone klucze nie są w poprawnym formacie."
                )
                return redirect('grade-poll-tickets-enter')
            except ValueError as e:
                messages.error(request, f"Niepoprawne klucze: {e}")
                return redirect('grade-poll-tickets-enter')

            entries = []
            for ticket, poll in correct_polls:
                _ = Submission.get_or_create(poll, ticket)
                entries.append(ticket)

            if failed_polls:
                failed_polls = map(lambda x: f"- {x}", failed_polls)
                messages.error(
                    request,
                    "Poniższe ankiety nie mogły zostać załadowane:<br>" +
                    "<br>".join(failed_polls)
                )

            if entries:
                self.request.session['grade_poll_tickets'] = entries

        return redirect('grade-poll-submissions')


class SubmissionEntry(UpdateView):
    """Allows the user to update and view his submission(s)."""

    template_name = 'poll/submission.html'
    model = Submission
    slug_field = 'submissions'
    form_class = SubmissionEntryForm

    def get(self, *args, **kwargs):
        """Checks whether any submissions are present in the session."""
        if 'grade_poll_tickets' in self.request.session:
            return super(SubmissionEntry, self).get(*args, **kwargs)
        return redirect('grade-poll-tickets-enter')

    def get_context_data(self, **kwargs):
        """Sets the variables used for templating."""
        context = super().get_context_data(**kwargs)
        context.update({
            'is_grade_active': check_grade_status(),
            'active_submission': self.active_submission,
            'current_index': self.current_index,
            'stats': SubmissionStats(self.submissions),
            'polls': self.submissions,
            'iterator': itertools.count(),
        })

        return context

    def get_form_kwargs(self):
        """Fetches the schema with answers that will be used to render the form."""
        kw = super().get_form_kwargs()
        submission = self.active_submission
        if submission:
            kw['jsonfields'] = submission.answers['schema']

        return kw

    def get_initial(self):
        """Populates the form with answers sent by the user in previous requests."""
        initial = super().get_initial()
        submission = self.active_submission

        for index, field in enumerate(submission.answers['schema']):
            field_name = f'field_{index}'
            initial[field_name] = submission.answers['schema'][index]['answer']

        return initial

    @property
    def active_submission(self):
        """Translates an index to the instance of requested Submission."""
        return self.submissions[self.current_index]

    @property
    def submissions(self) -> List[Submission]:
        """Fetches submissions from the database.

        This should be simplified by @cached_property decorator once we reach Python 3.8.
        """
        if hasattr(self, '_submissions'):
            return getattr(self, '_submissions')
        tickets = self.request.session['grade_poll_tickets']
        submissions = Submission.objects.filter(ticket__in=tickets)
        submissions = sorted(submissions, key=attrgetter('category'))
        setattr(self, '_submissions', submissions)
        return submissions

    @property
    def current_index(self):
        return int(self.kwargs['submission_index'])

    def get_object(self):
        return self.active_submission

    def get_success_url(self):
        """Manages how the user is redirected after submitting his answers.

        By default, when the form is validated successfully, the user
        is redirected to the next unfinished submission in the list.
        When no submissions are left, 0 is returned.
        """
        submissions = self.submissions
        submissions[self.current_index].submitted = True
        next_index = 0
        indexed = list(enumerate(submissions))
        for i, s in itertools.chain(indexed[self.current_index:], indexed[:self.current_index]):
            if not s.submitted:
                next_index = i
                break

        return reverse('grade-poll-submissions', kwargs={'submission_index': next_index})


class PollResults(TemplateView):
    """Displays results for all archived and submitted submissions."""

    template_name = 'poll/results.html'

    @staticmethod
    def __get_counter_for_categories(polls):
        number_of_submissions_for_category = defaultdict(int)
        for poll in polls:
            if poll:
                number_of_submissions_for_category[
                    poll.category
                ] += poll.number_of_submissions

        return number_of_submissions_for_category

    @staticmethod
    def __get_processed_results(submissions):
        poll_results = PollSummarizedResults(
            display_answers_count=True, display_plots=True
        )

        for submission in submissions:
            if 'schema' in submission.answers:
                for entry in submission.answers['schema']:
                    choices = None
                    if 'choices' in entry:
                        choices = entry['choices']
                    poll_results.add_entry(
                        question=entry['question'],
                        field_type=entry['type'],
                        answer=entry['answer'],
                        choices=choices,
                    )

        return poll_results

    def get(self, request, semester_id=None, poll_id=None, submission_id=None):
        """The main logic of passing data to the template presenting the results of the poll.

        :param semester_id: if given, fetches polls from requested semester.
        :param poll_id: if given, displays summary for a given poll.
        :param submission_id: if given, displays detailed submission view.
        """
        is_grade_active = check_grade_status()
        if semester_id is None:
            semester_id = Semester.get_current_semester().id
        current_semester = Semester.get_current_semester()

        try:
            selected_semester = Semester.objects.filter(pk=semester_id).get()
        except Semester.DoesNotExist:
            messages.error(
                request, "Wybrany semestr nie istnieje."
            )
            return redirect('grade-main')

        available_polls = Poll.get_all_polls_for_semester(
            user=request.user, semester=selected_semester
        )
        current_poll = Poll.objects.filter(id=poll_id).first()
        if poll_id is not None:
            submissions = Submission.objects.filter(poll=poll_id,
                                                    submitted=True).order_by('modified')
            if current_poll not in available_polls:
                # User does not have permission to view details about
                # the selected poll
                messages.error(
                    request, "Nie masz uprawnień do wyświetlenia tej ankiety."
                )
                return redirect('grade-poll-results', semester_id=semester_id)
        else:
            submissions = []

        semesters = Semester.objects.all()

        if request.user.is_superuser or request.user.employee:
            return render(
                request,
                self.template_name,
                {
                    'is_grade_active': is_grade_active,
                    'polls': group(entries=available_polls, sort=True),
                    'results': self.__get_processed_results(submissions),
                    'results_iterator': itertools.count(),
                    'semesters': semesters,
                    'current_semester': current_semester,
                    'current_poll_id': poll_id,
                    'current_poll': current_poll,
                    'selected_semester': selected_semester,
                    'submissions_count': self.__get_counter_for_categories(
                        available_polls
                    ),
                    'iterator': itertools.count(),
                },
            )

        messages.error(request, "Nie masz uprawnień do wyświetlania wyników oceny.")
        return redirect('grade-main')


class GradeDetails(TemplateView):
    """Displays details and rules about how the grade is set up."""

    template_name = 'poll/main.html'

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {'is_grade_active': is_grade_active})


class ClearSession(View):
    """Removes submissions from the active session."""

    def get(self, request):
        self.request.session.flush()
        messages.success(
            request,
            "Dziękujemy za wzięcie udziału w ocenie zajęć! "
            "Sesja została wyczyszczona.",
        )
        return redirect('grade-poll-tickets-enter')
