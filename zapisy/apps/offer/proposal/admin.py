"""Proposal admin configuration.
"""

from django.contrib import admin, messages

from .models import Proposal, ProposalStatus


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_filter = ('status', 'semester', 'course_type', ('owner', admin.RelatedOnlyFieldListFilter),
                   'modified', 'tags', 'effects')
    list_display = ('name', 'owner', 'course_type', 'semester', 'status', 'modified')
    search_fields = ('name', 'name_en')

    actions = ['reset_status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.select_related('owner__user', 'course_type')
        return qs

    def reset_status(self, request, queryset):
        """Resets the status of selected proposals from IN_VOTE to IN_OFFER.

        It will fail if any proposal with status different than IN_VOTE or
        IN_OFFER are selected.
        """
        if queryset.exclude(status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE]).exists():
            self.message_user(
                request, (f"Nie wykonano akcji. Tylko propozycje o "
                          f"statusie {ProposalStatus.IN_VOTE.display.upper()} "
                          "powinny być resetowane."),
                level=messages.WARNING)
            return
        num = queryset.update(status=ProposalStatus.IN_OFFER)
        self.message_user(request, f"Zmieniono status {num} propozycji", level=messages.SUCCESS)
    reset_status.short_description = (
        f"Resetuj status propozycji z "
        f"{ProposalStatus.IN_VOTE.display.upper()} do {ProposalStatus.IN_OFFER.display.upper()}")
