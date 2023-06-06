from .. import factories

from ...models import Schema, Poll


def add_submissions(poll_id, number_of_submissions):

    # Function is dedicated to adding submissions to requested poll.
    # 'Poll_id' can be found in keys to polls generated for student.
    # 'Number of submissions' specify how many submissions should be added to database.
    # Be aware that submission added this way won't be preserved between vagrant sessions.
    # You can find instruction how achive persistency by saving database snapshot on wiki.
    # Instruction how run code on virtual machine also can be found on wiki.

    polls = Poll.objects.filter(id=poll_id)
    if len(polls) != 1:
        print(f"Searching for poll failed, found {len(polls)} matching polls")
        return

    poll = polls[0]
    schema = Schema.get_latest(poll_type=poll.type)
    factories.SubmissionFactory.create_batch(number_of_submissions, schema=schema, poll=poll)
