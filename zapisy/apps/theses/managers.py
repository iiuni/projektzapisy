"""Defines a custom Theses manager for use by the Rest API,
with prefetching and several common filters
"""
from typing import List

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Value, When, Case, BooleanField, QuerySet, Q
from django.db.models.functions import Concat, Lower
from django.db.models.expressions import RawSQL

from apps.users.models import BaseUser
from .enums import (
    ThesisKind, ThesisStatus, ThesisTypeFilter, ThesisVote,
    ENGINEERS_KINDS, BACHELORS_KINDS, BACHELORS_OR_ENGINEERS_KINDS,
    ISIM_KINDS, NOT_READY_STATUSES
)


class APIQueryset(models.QuerySet):
    def filter_available(self: QuerySet) -> QuerySet:
        """Returns only theses that are considered "available" from the specified queryset"""
        return self.exclude(
            status=ThesisStatus.IN_PROGRESS
        ).exclude(_is_archived=True).filter(reserved_until__isnull=True)

    def filter_by_type(self: QuerySet, thesis_type: ThesisTypeFilter, user: User) -> QuerySet:
        """Returns only theses matching the specified type filter from the specified queryset"""
        if thesis_type == ThesisTypeFilter.EVERYTHING:
            return self
        elif thesis_type == ThesisTypeFilter.CURRENT:
            return self.exclude(_is_archived=True)
        elif thesis_type == ThesisTypeFilter.ARCHIVED:
            return self.filter(_is_archived=True)
        elif thesis_type == ThesisTypeFilter.MASTERS:
            return self.filter(kind=ThesisKind.MASTERS)
        elif thesis_type == ThesisTypeFilter.ENGINEERS:
            return self.filter(kind__in=ENGINEERS_KINDS)
        elif thesis_type == ThesisTypeFilter.BACHELORS:
            return self.filter(kind__in=BACHELORS_KINDS)
        elif thesis_type == ThesisTypeFilter.BACHELORS_OR_ENGINEERS:
            return self.filter(kind__in=BACHELORS_OR_ENGINEERS_KINDS)
        elif thesis_type == ThesisTypeFilter.ISIM:
            return self.filter(kind__in=ISIM_KINDS)
        elif thesis_type == ThesisTypeFilter.AVAILABLE_MASTERS:
            return self.filter(kind=ThesisKind.MASTERS).filter_only_available()
        elif thesis_type == ThesisTypeFilter.AVAILABLE_ENGINEERS:
            return self.filter(kind__in=ENGINEERS_KINDS).filter_only_available()
        elif thesis_type == ThesisTypeFilter.AVAILABLE_BACHELORS:
            return self.filter(kind__in=BACHELORS_KINDS).filter_only_available()
        elif thesis_type == ThesisTypeFilter.AVAILABLE_BACHELORS_OR_ENGINEERS:
            return self.filter(kind__in=BACHELORS_OR_ENGINEERS_KINDS).filter_only_available()
        elif thesis_type == ThesisTypeFilter.AVAILABLE_ISIM:
            return self.filter(kind__in=ISIM_KINDS).filter_only_available()
        elif thesis_type == ThesisTypeFilter.UNGRADED:
            return self.filter_only_ungraded(user)
        # Should never get here
        return self

    def filter_only_available(self: QuerySet):
        """Returns only theses that are considered "available"
        """
        return self.exclude(
            status=ThesisStatus.IN_PROGRESS
        ).exclude(_is_archived=True).filter(reserved_until__isnull=True)

    def filter_by_user(self: QuerySet, user: User):
        """Filter the queryset based on special logic depending
        on the type of the user
        """
        # Students should not see theses that are not "ready" yet
        if BaseUser.is_student(user):
            return self.exclude(status__in=NOT_READY_STATUSES)
        return self

    def filter_by_title(self: QuerySet, title: str):
        return self.filter(title__icontains=title)

    def filter_by_advisor(self: QuerySet, advisor: str):
        return self.filter(_advisor_name__icontains=advisor)

    def filter_only_mine(self: QuerySet, user: User):
        if BaseUser.is_student(user):
            return self.filter(students__in=[user.student])
        elif BaseUser.is_employee(user):
            return self.filter(Q(advisor=user.employee) | Q(supporting_advisor=user.employee))
        # this is an error situation, one of the conditions above should have caught it
        return self

    def filter_only_ungraded(self: QuerySet, voter: User):
        """
        Filter the given queryset to only contain
        all _ungraded_ theses for a given board member.
        A thesis is _ungraded_ if the voter has not cast a vote at all
        or manually set it to none (not possible from the client UI currently).
        The `voter` user must be a theses board member.
        """
        # Uses custom SQL - I couldn't get querysets to do what I wanted them to;
        # doing .exclude(votes__value__ne=none, votes__voter=emp) doesn't do what you want,
        # it ands two selects together rather than and two conditions in one select
        return self.filter(
            # While voting for rejected theses is allowed, they're not "priority",
            # so we don't count them here
            status=ThesisStatus.BEING_EVALUATED
        ).annotate(definite_votes=RawSQL(
            """
            select count(*) from theses_thesisvotebinding where
            thesis_id=theses_thesis.id and voter_id=%s and value<>%s
            """,
            (voter.employee.pk, ThesisVote.NONE.value)
        )).filter(definite_votes=0)

    def sort(self: QuerySet, sort_column: str, sort_dir: str) -> QuerySet:
        """Sort the specified queryset first by archived status (unarchived theses first),
        then by the specified column in the specified direction,
        or by newest first if not specified
        """
        db_column = ""
        if sort_column == "advisor":
            db_column = "_advisor_name"
        elif sort_column == "title":
            db_column = "title"

        resulting_ordering = "-modified"
        if db_column:
            orderer = Lower(db_column)
            resulting_ordering = orderer.desc() if sort_dir == "desc" else orderer.asc()

        # We want to first order by archived
        return self.order_by("_is_archived", resulting_ordering)


class APIManager(models.Manager):
    def get_queryset(self):
        """Return theses queryset with the appropriate fields prefetched (see fields_for_prefetching)
        as well as user names annotated for further processing - sorting/filtering
        """
        return APIQueryset(self.model, using=self._db).select_related(
            *APIManager.fields_for_prefetching("advisor"),
            *APIManager.fields_for_prefetching("supporting_advisor"),
        ).prefetch_related(
            "students",
            "votes",
            "votes__voter"
        ).annotate(
            _advisor_name=Concat(
                "advisor__user__first_name", Value(" "), "advisor__user__last_name"
            )
        ).annotate(_is_archived=Case(
            When(status=ThesisStatus.DEFENDED, then=True),
            default=Value(False),
            output_field=BooleanField()
        ))

    @staticmethod
    def fields_for_prefetching(base_field: str) -> List[str]:
        """For all user fields present on the thesis, we need to prefetch
        both our user model and the standard Django user it's linked to,
        since basic user information needed when serializing is defined there.
        """
        return [base_field, f'{base_field}__user']
