from django.db.models.signals import post_save
from django.dispatch import receiver

from .enums import ThesisVote, ThesisStatus
from .models import Vote
from .system_settings import get_num_required_votes

from apps.notifications.custom_signals import thesis_accepted


@receiver(post_save, sender=Vote)
def auto_accept(sender, instance: Vote, **kwargs):
    """Accepts thesis when enough accepting votes have been submitted."""
    thesis = instance.thesis
    vote = instance.vote
    import logging
    print("vote before submit")
    logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('This is an info message')
    if vote == ThesisVote.ACCEPTED and thesis.get_accepted_votes() >= get_num_required_votes():
        print("vote submitted")
        if thesis.has_no_students_assigned:
            thesis.status = ThesisStatus.ACCEPTED
            thesis_accepted.send(sender=Vote, instance=thesis)
            
            logger.debug('This is a debug message')

            print("sending accepted")
        else:
            thesis.status = ThesisStatus.IN_PROGRESS
        thesis.save()
