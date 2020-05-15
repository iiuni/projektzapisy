from collections import defaultdict, namedtuple
from typing import Dict, List, Tuple

import bokeh.embed
import bokeh.models.sources
import bokeh.plotting

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll, Submission
from apps.users.models import Student

SubmissionWithStatus = namedtuple('SubmissionWithStatus', ['submission', 'submitted'])

GroupedSubmissions = namedtuple(
    'GroupedSubmissions',
    [
        'with_categories',
        'statuses',
        'submitted',
        'total',
        'progress',
        'progress_numerical',
    ],
)


def check_grade_status() -> bool:
    """Checks whether any of the semesters has grade enabled."""
    current_semester = Semester.get_current_semester()
    return current_semester.is_grade_active


def get_grouped_polls(student: Student) -> Dict:
    """Groups polls into a format used by the grade/ticket_create app."""
    polls = Poll.get_all_polls_for_student(student)

    return group_submissions(polls)


def group_submissions_with_statuses(
    submissions: List[SubmissionWithStatus]
) -> Tuple[dict, dict]:
    """Groups submissions into a structure that is useful for templating.

    Fields are defined in a `GroupedSubmissions` namedtuple.
    """
    grouped_submissions = defaultdict(list)
    submitted_statuses = defaultdict(int)
    submitted_count = 0

    for submission_with_status in submissions:
        submission, status = submission_with_status
        category = submission.category
        if category not in submitted_statuses:
            submitted_statuses[category] = 0
        grouped_submissions[category].append(submission_with_status)
        if status:
            submitted_statuses[category] += 1
            submitted_count += 1

    return GroupedSubmissions(
        with_categories=dict(grouped_submissions),
        statuses=dict(submitted_statuses),
        submitted=submitted_count,
        total=len(submissions),
        progress=f"{submitted_count} / {len(submissions)}",
        progress_numerical=submitted_count / len(submissions),
    )


def group_submissions(submissions: List[Submission]) -> dict:
    """Groups a list of submissions into a dictionary.

    The submissions are transformed into a dictionary of nested categories and
    subcategories.

    This method is structuring data that allows for easy displaying
    handly tables in views such as the one responsible for summarizing
    the results of students' submissions.
    """
    grouped_submissions = defaultdict(list)

    for submission in submissions:
        category = submission.category
        subcategory = submission.subcategory
        if subcategory not in grouped_submissions[category]:
            grouped_submissions[category].append(subcategory)

    grouped_submissions = dict(sorted(grouped_submissions.items()))

    return grouped_submissions


def group(entries: List[Poll], sort=False) -> dict:
    """Groups a list of polls/submissions into a dictionary.

    The polls and submissions are combined into a dictionary of nested
    categories and original entries.

    This method is structuring data that allows for easy displaying
    handly tables in views such as the one responsible for summarizing
    the results of students' submissions.
    """
    grouped_entries = defaultdict(list)
    output = defaultdict(list)

    for entry in entries:
        if entry is not None:
            category = entry.category
            subcategory = entry.subcategory
            if subcategory not in grouped_entries[category]:
                if entry.semester:  # whether the entry is a general poll
                    output[category].append(entry)
                grouped_entries[category].append(entry)

    if sort:
        grouped_entries = sorted(grouped_entries.items())

    output.update(grouped_entries)

    return dict(output)


class PollSummarizedResultsEntry:
    """A single entry in a summary view for a Poll.

    Contains a question, answers and possible choices (if defined).
    Allows for easy plotting the provided data.
    """
    def __init__(self, question, field_type, choices=None):
        self.question = question
        self._answers = []
        self._choices = choices
        self._choices_occurences = [0] * len(choices) if choices else []
        self._components = None
        self.field_type = field_type

    @property
    def field_choices(self):
        """Lists all possible answers that could be selected for radio fields."""
        if self.field_type == 'radio':
            return self._choices
        if self.field_type == 'checkbox':
            return self._choices
        return []

    def add_answer(self, answer):
        """Adds an answer to the container.

        If the field_type of the entry is set to `radio`, the answer will be
        counted if and only if it is present in the set of predefined choices.
        If the field_tyoe of the entry is set to `checkbox`, each answer will be
        counted separately.
        """
        if not answer:
            return
        if self.field_type == 'radio' and answer in self._choices:
            choice_index = self._choices.index(answer)
            self._choices_occurences[choice_index] += 1
        if self.field_type == 'checkbox':
            # Multiple-choice question will have a list of selected answers.
            for a in answer:
                choice_index = self._choices.index(a)
                self._choices_occurences[choice_index] += 1
        self._answers.append(answer)

    @property
    def answers(self):
        return self._answers

    @property
    def plot(self):
        """Generates an embeddable plot.

        https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html#components

        :returns: a tuple of (javascript code, html code) that can be
            used for embedding plots in the template.
        """
        if not self._components:
            plot = bokeh.plotting.figure(
                y_range=self._choices,
                sizing_mode='scale_width',
                plot_height=250,
                toolbar_location=None,
                tools='',
            )

            source = bokeh.models.sources.ColumnDataSource(
                data=dict(choices=self._choices, values=self._choices_occurences)
            )

            plot.hbar(y='choices', right='values', source=source, height=0.8)
            plot.x_range.start = 0
            plot.axis.minor_tick_line_color = None

            self._components = bokeh.embed.components(plot)

        return self._components


class PollSummarizedResults:
    """Container for all sections (entries) in the summary results view of the Poll.

    A single section is also a self-contained entry, defined by
    the `PollSummarizedResultsEntry` class.
    """
    def __init__(self, display_answers_count=True, display_plots=True):
        self._entries = []
        self._questions = []
        self.display_answers_count = display_answers_count
        self.display_plots = display_plots

    def add_entry(self, question, field_type, answer, choices=None):
        if question in self._questions:
            index = self._questions.index(question)
            existing_entry = self._entries[index]
            existing_entry.add_answer(answer)
        else:
            new_entry = PollSummarizedResultsEntry(
                question=question, field_type=field_type, choices=choices
            )
            new_entry.add_answer(answer)
            self._entries.append(new_entry)
            self._questions.append(question)

    def add_choices(self, choices):
        self._choices = choices

    @property
    def entries(self):
        return self._entries
