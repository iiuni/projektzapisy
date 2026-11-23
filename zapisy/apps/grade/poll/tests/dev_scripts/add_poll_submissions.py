from .. import factories

from ...models import Schema, Poll


def add_submissions(poll_id, number_of_submissions):
    """Function is dedicated to adding submissions to requested poll.

    :param poll_id: primary key of poll, can be found i.e. in url of page with poll results.
    :param number_of_submissions: specify how many submissions should be added to database.
    Be aware that submission added this way won't be preserved between vagrant sessions.
    You can find instructions on achieving persistence by saving database snapshots on wiki:
    https://github.com/iiuni/projektzapisy/wiki/Tworzenie-dumpa-bazy-danych-zmodyfikowanej-w-trakcie-sesji-vagranta
    Instruction on how to run a code on a virtual machine can also be found on the wiki:
    https://github.com/iiuni/projektzapisy/wiki/Na-co-uwa%C5%BCa%C4%87-przy-programowaniu%3F
    """
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise AttributeError(f"Poll with id={poll_id} does not exists.")

    schema = Schema.get_latest(poll_type=poll.type)
    factories.SubmissionFactory.create_batch(number_of_submissions, schema=schema, poll=poll)
