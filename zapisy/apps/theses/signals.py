from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.custom_signals import thesis_accepted
from .enums import ThesisVote, ThesisStatus
from .models import Vote
from .system_settings import get_num_required_votes


@receiver(post_save, sender=Vote)
def auto_accept(sender, instance: Vote, **kwargs):
    """Accepts thesis when enough accepting votes have been submitted."""
    thesis = instance.thesis
    vote = instance.vote
    if vote == ThesisVote.ACCEPTED and thesis.get_accepted_votes() >= get_num_required_votes():
        if thesis.has_no_students_assigned:
            thesis.status = ThesisStatus.ACCEPTED
        else:
            thesis.status = ThesisStatus.IN_PROGRESS
        thesis_accepted.send(sender=Vote, instance=thesis)
        thesis.save()
