from functools import cmp_to_key
from string import whitespace
from math import gcd
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random.random import getrandbits, randint
from Crypto.Signature import pkcs1_15
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import PublicKey, PrivateKey, \
    UsedTicketStamp
from django.utils.safestring import SafeText

RAND_BITS = 512
KEY_LENGTH = 1024


def poll_cmp(poll1, poll2):
    if poll1.group:
        if poll2.group:
            c = cmp(poll1.group.course.name, poll2.group.course.name)
            if c == 0:
                c = cmp(poll1.group.type, poll2.group.type)
                if c == 0:
                    if poll1.studies_type:
                        if poll2.studies_type:
                            c = cmp(poll1.studies_type, poll2.studies_type)
                            if c == 0:
                                return cmp(poll1.title, poll2.title)
                            else:
                                return c
                        else:
                            return 1
                    else:
                        if poll2.studies_type:
                            return -1
                        else:
                            return cmp(poll1.title, poll2.title)
                else:
                    return c
            else:
                return c
        else:
            return 1
    else:
        if poll2.group:
            return -1
        else:
            if poll1.studies_type:
                if poll2.studies_type:
                    c = cmp(poll1.studies_type, poll2.studies_type)
                    if c == 0:
                        return cmp(poll1.title, poll2.title)
                    else:
                        return c
                else:
                    return 1
            else:
                if poll2.studies_type:
                    return -1
                else:
                    return cmp(poll1.title, poll2.title)


def cmp(a, b):
    """
    Since there is no cmp in python 3 documentation suggests this expression to
    emulate the feature
    :param a:
    :param b:
    :return:
    """
    return (a > b) - (b < a)


def generate_rsa_key():
    """
        Generates RSA key - that is, a pair (public key, private key)
        both exported in PEM format
    """
    rsa_key = RSA.generate(KEY_LENGTH)
    private_key = rsa_key.exportKey()
    public_key = rsa_key.publickey().exportKey()
    return public_key, private_key


def save_keys(keys_list):
    """
        Saves generated key to database into PrivateKey and PublicKey models
        :param keys_list: list of key pairs with poll in format (poll, public key, private key)
    """
    for (poll, pub, priv) in keys_list:
        private_key = PrivateKey(poll=poll, private_key=priv)
        public_key = PublicKey(poll=poll, public_key=pub)
        private_key.save()
        public_key.save()


def generate_keys_for_polls(semester=None):
    # TODO check if keys exist
    """
    Generates RSA key pair for each poll in given semester
    :param semester: if none then current semester is taken
    """
    if not semester:
        semester = Semester.get_current_semester()
    poll_list = Poll.get_polls_without_keys(semester)
    key_list = []
    i = 1
    for poll in poll_list:
        (pub, priv) = generate_rsa_key()
        key_list.append((poll, pub, priv))
        i = i + 1
    save_keys(key_list)
    return i - 1


def group_polls_by_course(poll_list):
    """
    Groups polls into lists by course and returns them inside list
    :param poll_list: list of polls
    :return: list of list of polls grouped by course
    """
    if not poll_list:
        return []

    poll_list.sort(key=cmp_to_key(poll_cmp))

    res = []
    act_polls = []
    act_group = poll_list[0].group

    for poll in poll_list:
        if not act_group:
            if not poll.group:
                act_polls.append(poll)
            else:
                act_group = poll.group
                res.append(act_polls)
                act_polls = [poll]
        else:
            if poll.group:
                if act_group.course == poll.group.course:
                    act_polls.append(poll)
                else:
                    act_group = poll.group
                    res.append(act_polls)
                    act_polls = [poll]
            else:
                act_group = poll.group
                res.append(act_polls)
                act_polls = [poll]

    res.append(act_polls)

    return res


def connect_groups(grouped_polls, form):
    """

    :param grouped_polls: list of grouped polls by course
    :param form: form
    :return: polls with connections
    """
    connected_groups = []
    for polls in grouped_polls:
        if not polls[0].group:
            label = 'join_common'
        else:
            label = 'join_' + str(polls[0].group.course.pk)

        if len(polls) == 1:
            connected_groups.append(polls)
        elif form.cleaned_data[label]:
            connected_groups.append(polls)
        else:
            for poll in polls:
                connected_groups.append([poll])

    return connected_groups


"""
Functions below implement blind signature protocol
"""


def is_poll_visible(user, poll):
    """
    Checks, whether user is a student entitled to the poll.
    """
    if hasattr(user, "student") and user.student:
        return poll.is_student_entitled_to_poll(user.student)
    else:
        return False


def is_ticket_signed(user, poll):
    """
    Checks, if the user is a student with a yet unused ticket for the poll.
    """
    if hasattr(user, "student") and user.student:
        u = UsedTicketStamp.objects.filter(student=user.student, poll=poll)
        return True if u else False
    else:
        return False


def mark_poll_used(user, poll):
    """Saves the user's stamp for the poll.

    :raises:
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp(student=user.student, poll=poll)
    u.save()


def get_valid_tickets(ticket_list):
    """
    Returns the list of valid tickets and list of errors
    :param ticket_list list of tickets from user input
    :return list of errors and list of tickets
    """
    err = []
    val = []
    for group, ticket, st in ticket_list:
        if st == "Nie jesteś przypisany do tej ankiety" or \
                st == "Bilet już pobrano":
            err.append((str(group), st))
        else:
            val.append((group, ticket, st))
    return err, val


def secure_signer_without_save(user, poll, ticket):
    """
    :param user: user to be checked against poll
    :param poll: poll to verify
    :param ticket: ticket for verification
    :return: either signed ticket or one of error strings:
    "Nie jesteś przypisany do tej ankiety", "Bilet już pobrano"
    """
    if not is_poll_visible(user, poll):
        return "Nie jesteś przypisany do tej ankiety"
    if is_ticket_signed(user, poll):
        return "Bilet już pobrano"

    key = PrivateKey.objects.get(poll=poll)
    return sign_ticket(ticket, key)


# FIXME the return type of this method is due to legacy ticket
# handling code in ticket_create/views and poll/utils
def sign_ticket(ticket, priv_key):
    """
        Signs ticket using private key
    :param ticket: ticket to be signed
    :param priv_key: RSA private key
    :return: signed ticket as int
    """
    priv = RSA.importKey(priv_key.private_key)
    ticket_hash = SHA256.new(ticket.encode("utf-8"))
    signed = pkcs1_15.new(priv).sign(ticket_hash)
    signed_as_int = _int_from_bytes(signed)
    return signed_as_int


def _int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def convert_ticket_record(ticket):
    """
    Converts record:
        id: XYZ
        TICKET
    to pair (id, TICKET)
    :param ticket: ticket to convert
    :return: result pair
    """
    t = ticket.strip().split('\r\n')
    if len(t) > 1:
        poll_id = str(t[0]).strip().split('id:')[1]
        return int(poll_id), str(t[1]).strip()


class Signature:
    """
        Model for signed_tickets.html
    """

    def __init__(self, poll_id, sign):
        self.poll_id = poll_id
        self.signature = sign


"""Legacy, needs to be here till we refactor voting - pycryptodome does not support blinding natively"""


def generate_ticket(poll_list):
    """
    Generates tickets for polls
    :param poll_list: list of polls for generation
    :return: list of tickets
    """
    m = getrandbits(RAND_BITS)
    blinded = []

    for poll in poll_list:
        key = RSA.importKey(PublicKey.objects.get(poll=poll).public_key)
        n = key.n
        e = key.e
        k = randint(2, n)

        while gcd(n, k) != 1:
            k = randint(1, n)

        a = (m % n)
        b = pow(k, e, n)
        t = (a * b) % n

        blinded.append((poll, t))
    return blinded


def to_plaintext(ticket_list):
    """
    Converts recorts to plaintext for user
    :param ticket_list: list of tickets with polls and their signatures
    :return: pretty printed version of tickets
    """
    res = ""
    for poll, ticket, signed_ticket in ticket_list:
        res += '[' + poll.title + ']'
        if not poll.group:
            res += 'Ankieta ogólna &#10;'
        else:
            res += str(poll.group.course.name) + " &#10;"
            res += str(poll.group.get_type_display()) + ": "
            res += str(poll.group.get_teacher_full_name()) + " &#10;"
        if poll.studies_type:
            res += 'typ studiów: ' + str(poll.studies_type) + " &#10;"

        res += 'id: ' + str(poll.pk) + ' &#10;'
        res += str(ticket) + " &#10;"
        res += str(signed_ticket) + " &#10;"
        res += "---------------------------------- &#10;"
    return SafeText(str(res))


# FIXME explanation of ticket parsing code: str(int())
# The list is split into chunks, some of which are empty, and some of which
# contain the tickets we want (e.g. ['123123', '', '', 'somecrap', '321321'])
# The list is iterated until doing int(list[i]) succeeds; at this point
# it's assumed we've found the key. However, we actually want to return
#  the tickets as strings, not ints.
# This entire function should be rewritten from scratch
def from_plaintext(tickets_plaintext):
    """
    Converts printed version of tickets to list of poll ids, tickets and their signatures
    :param tickets_plaintext: list of tickets
    :return: converted tickets
    """
    pre_tickets = tickets_plaintext.split('----------------------------------')
    pre_tickets = [[x] for x in pre_tickets]
    for sign in whitespace:
        pre_tickets = [flatten(
            [x.split(sign) for x in ls]) for ls in pre_tickets]

    convert = False
    ids_tickets_signed = []
    for poll_info in pre_tickets:
        i = 0
        while i < len(poll_info):
            if convert:
                j = i
                id = -1
                t = -1
                st = -1
                while True:
                    try:
                        id = int(poll_info[j])
                        break
                    except BaseException:
                        j += 1

                j += 1
                while True:
                    try:
                        t = str(int(poll_info[j]))
                        break
                    except BaseException:
                        j += 1

                j += 1
                while True:
                    try:
                        st = int(poll_info[j])
                        break
                    except BaseException:
                        j += 1

                i = j + 1
                convert = False
                ids_tickets_signed.append((id, (t, st)))
            elif poll_info[i].startswith('id:'):
                convert = True
            i += 1

    return ids_tickets_signed


def flatten(x):
    result = []
    for el in x:
        if isinstance(el, list):
            if hasattr(el, "__iter__") and not isinstance(el, str):
                result.extend(flatten(el))
            else:
                result.append(el)
        else:
            result.append(el)

    return result


def gcwd(u, v):
    u1 = 1
    u2 = 0
    u3 = u
    v1 = 0
    v2 = 1
    v3 = v
    while v3 != 0:
        q = u3 / v3
        t1 = u1 - q * v1
        t2 = u2 - q * v2
        t3 = u3 - q * v3
        u1 = v1
        u2 = v2
        u3 = v3
        v1 = t1
        v2 = t2
        v3 = t3
    return u1, u2, u3
