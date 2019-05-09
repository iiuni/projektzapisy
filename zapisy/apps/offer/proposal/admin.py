"""Proposal admin configuration.
"""

from django.contrib import admin, messages
from django.db import models

from apps.enrollment.courses.models import Semester

from .models import Proposal, ProposalStatus


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_filter = ('status', 'semester', 'course_type', ('owner', admin.RelatedOnlyFieldListFilter),
                   'modified', 'tags', 'effects', ('entity__course__semester',
                                                   admin.RelatedOnlyFieldListFilter))
    list_display = ('name', 'owner', 'course_type', 'semester', 'status', 'modified',
                    'last_semester')
    search_fields = ('name', 'name_en')

    actions = [
        'move_into_offer',
        'withdraw_proposals',
        'put_under_vote',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('owner__user', 'course_type')
        qs = qs.prefetch_related('entity__course_set__semester')

        # Every proposal will be annotated with last semester, when it was
        # conducted.
        last_semester_agg = models.Max('entity__course__semester')
        qs = qs.annotate(_last_semester=last_semester_agg)

        return qs

    def last_semester(self, obj):
        """Transforms the id of last semester into a proper object."""
        # Load all semesters into memory once instead of querying them by id
        # separately.
        if getattr(self, 'semesters', None) is None:
            self.semesters = {s.id: s for s in Semester.objects.all()}
        if obj._last_semester is None:
            return None
        return self.semesters[obj._last_semester]
    last_semester.short_description = "Ostatni semestr"
    last_semester.admin_order_field = '_last_semester'

    def move_into_offer(self, request, queryset):
        """Changes the status of selected proposals to IN_OFFER.

        It will fail if any proposal with status different than IN_VOTE,
        IN_OFFER, or PROPOSAL are selected.
        """
        allowed_statuses = [
            ProposalStatus.PROPOSAL, ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE
        ]
        if queryset.exclude(status__in=allowed_statuses).exists():
            message = (f"Nie wykonano akcji. Tylko propozycje o statusie "
                       f"{ProposalStatus.PROPOSAL.display.upper()} lub "
                       f"{ProposalStatus.IN_VOTE.display.upper()} powinny być "
                       "przenoszone do oferty.")
            self.message_user(request, message, level=messages.WARNING)
            return
        num = queryset.update(status=ProposalStatus.IN_OFFER)
        message = f"Przeniesiono {num} propozycji do oferty."
        self.message_user(request, message, level=messages.SUCCESS)
    move_into_offer.short_description = (
        f"Zmień status wybranych propozycji na {ProposalStatus.IN_OFFER.display.upper()}")

    def withdraw_proposals(self, request, queryset):
        """Changes the status of selected proposals to WITHDRAWN."""
        allowed_statuses = [
            ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE, ProposalStatus.WITHDRAWN
        ]
        if queryset.exclude(status__in=allowed_statuses).exists():
            self.message_user(request, ("Nie wykonano akcji. Tylko propozycje będące w ofercie "
                                        "powinny być z niej wycofywane."),
                              level=messages.WARNING)
            return
        num = queryset.update(status=ProposalStatus.WITHDRAWN)
        self.message_user(request, f"Wycofano z oferty {num} propozycji", level=messages.SUCCESS)
    withdraw_proposals.short_description = (
        f"Zmień status wybranych propozycji na {ProposalStatus.WITHDRAWN.display.upper()}")

    def put_under_vote(self, request, queryset):
        """Changes the status of selected proposals to IN_VOTE."""
        allowed_statuses = [ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE]
        if queryset.exclude(status__in=allowed_statuses).exists():
            self.message_user(request, ("Nie wykonano akcji. Tylko propozycje będące w ofercie "
                                        "mogą być poddawane pod głosowanie."),
                              level=messages.WARNING)
            return
        num = queryset.update(status=ProposalStatus.IN_VOTE)
        self.message_user(request,
                          f"Przeniesiono pod głosowanie {num} propozycji",
                          level=messages.SUCCESS)
    put_under_vote.short_description = (
        f"Zmień status wybranych propozycji na {ProposalStatus.IN_VOTE.display.upper()}")
