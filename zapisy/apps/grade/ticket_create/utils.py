# -*- coding: utf-8 -*-
from string import whitespace

from Crypto.PublicKey import RSA
from Crypto.Random.random import getrandbits, \
    randint
from apps.enrollment.courses.models import Semester
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.exceptions import *
from apps.grade.ticket_create.models import PublicKey, \
    PrivateKey, \
    UsedTicketStamp
from django.contrib.admin.utils import flatten
from django.utils.safestring import SafeUnicode

RAND_BITS = 512
KEY_LENGTH = 1024

"""
1. W przeglądarce jest wygenrowane 512 rand bitów m - kuponik
2. Wylosowana jest liczba k względnie pierwsza z n
3. Szyfrujemy m za pomocą klucza publicznego
4. Wysyłamy do podpisu kluczem prywatnym
"""


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
    print i - 1
    return


def group_polls_by_course(poll_list):
    if not poll_list:
        return []

    poll_list.sort(poll_cmp)

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


def connect_groups(groupped_polls, form):
    connected_groups = []
    for polls in groupped_polls:
        if not polls[0].group:
            label = 'join_common'
        else:
            label = u'join_' + unicode(polls[0].group.course.pk)

        if len(polls) == 1:
            connected_groups.append(polls)
        elif form.cleaned_data[label]:
            connected_groups.append(polls)
        else:
            for poll in polls:
                connected_groups.append([poll])

    return connected_groups


def generate_keys(poll_list):
    keys = []

    for poll in poll_list:
        key = RSA.importKey(PublicKey.objects.get(poll=poll).public_key)
        keys.append((unicode(key.n), unicode(key.e)))

    return keys


def check_poll_visiblity(user, poll):
    """Checks, whether user is a student entitled to the poll.

    Raises:
        InvalidPollException: If the user in question is not entitled to the
            poll.
        Student.DoesNotExist: If the user in question is not a student.
    """
    if not poll.is_student_entitled_to_poll(user.student):
        raise InvalidPollException


def check_ticket_not_signed(user, poll):
    """Checks, if the user is a student with a yet unused ticket for the poll.

    Raises:
        TicketUsed: If the user has already used the ticket for the poll.
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp.objects.filter(student=user.student, poll=poll)
    if u:
        raise TicketUsed


def mark_poll_used(user, poll):
    """Saves the user's stamp for the poll.

    Raises:
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp(student=user.student,
                        poll=poll)
    u.save()


def ticket_check_and_mark(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    mark_poll_used(user, poll)


def ticket_check_and_sign(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    key = PrivateKey.objects.get(poll=poll)
    signed = key.sign_ticket(ticket)
    mark_poll_used(user, poll)


def ticket_check_and_sign_without_mark(user, poll, ticket):
    check_poll_visiblity(user, poll)
    check_ticket_not_signed(user, poll)
    key = PrivateKey.objects.get(poll=poll)
    signed = key.sign_ticket(ticket)
    return signed


def secure_signer_without_save(user, g, t):
    try:
        return ticket_check_and_sign_without_mark(user, g, t),
    except InvalidPollException:
        return u"Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return u"Bilet już pobrano",


def secure_mark(user, g, t):
    try:
        return ticket_check_and_mark(user, g, t),
    except InvalidPollException:
        return u"Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return u"Bilet już pobrano",


def secure_signer(user, g, t):
    try:
        return ticket_check_and_sign(user, g, t),
    except InvalidPollException:
        return u"Nie jesteś przypisany do tej ankiety",
    except TicketUsed:
        return u"Bilet już pobrano",


def unblind(poll, st):
    st = st[0]
    if st == u"Nie jesteś przypisany do tej ankiety":
        return st
    elif st == u"Bilet już pobrano":
        return st
    else:
        st = st[0]
        key = RSA.importKey(PublicKey.objects.get(poll=poll).public_key)
        return (unicode(st), unicode(key.n), unicode(key.e))


def get_valid_tickets(tl):
    err = []
    val = []
    for g, t, st in tl:
        if st == u"Nie jesteś przypisany do tej ankiety" or \
                st == u"Bilet już pobrano":
            err.append((unicode(g), st))
        else:
            val.append((g, t, st))

    return err, val


def to_plaintext(vtl):
    res = ""
    for p, t, st in vtl:
        res += '[' + p.title + ']'
        if not p.group:
            res += u'Ankieta ogólna &#10;'
        else:
            res += unicode(p.group.course.name) + " &#10;"
            res += unicode(p.group.get_type_display()) + ": "
            res += unicode(p.group.get_teacher_full_name()) + " &#10;"
        if p.studies_type:
            res += u'typ studiów: ' + unicode(p.studies_type) + " &#10;"

        res += u'id: ' + unicode(p.pk) + ' &#10;'
        res += unicode(t) + " &#10;"
        res += unicode(st) + " &#10;"
        res += "---------------------------------- &#10;"
    return SafeUnicode(unicode(res))


def from_plaintext(tickets_plaintext):
    pre_tickets = tickets_plaintext.split('----------------------------------')
    pre_tickets = map(lambda x: [x], pre_tickets)
    for sign in whitespace:
        pre_tickets = map(lambda ls:
                          flatten(
                              map(
                                  lambda x:
                                  x.split(sign),
                                  ls)),
                          pre_tickets)

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
                    except:
                        j += 1

                j += 1
                while True:
                    try:
                        t = long(poll_info[j])
                        break
                    except:
                        j += 1

                j += 1
                while True:
                    try:
                        st = long(poll_info[j])
                        break
                    except:
                        j += 1

                i = j + 1
                convert = False
                ids_tickets_signed.append((id, (t, st)))
            elif poll_info[i].startswith('id:'):
                convert = True
            i += 1

    return ids_tickets_signed


def generate_ticket(poll_list):
    # TODO: Docelowo ma być po stronie przeglądarki
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
        b = expMod(k, e, n)
        t = (a * b) % n

        blinded.append((poll, t, (m, k)))
    return blinded


def blind_ticket(ticket, pub_key, k):
    return pub_key.blind(ticket, k)


def sign_ticket(ticket, priv_key):
    priv = RSA.importKey(priv_key.private_key)
    return priv.sign(ticket, 0)[0]


def unblind_ticket(ticket, priv_key, k):
    return priv_key.unblind(ticket, k)


def verify_ticket(ticket, signature, priv_key):
    return priv_key.verify(ticket, (signature,))


def convert_ticket_record(ticket):
    """
    This function converts ticket in form of:
        poll_id: XYZ
        TICKET
    to pair (poll_id, TICKET)
    :param ticket: ticket submitted from client to sign
    :return: ticket converted to pair
    """
    t = ticket.strip().split('\r\n')
    if len(t) > 1:
        poll_id = str(t[0]).strip().split('poll_id:')[1]
        return int(poll_id), str(t[1]).strip()


class Signature:
    def __init__(self, poll_id, sign):
        self.poll_id = poll_id
        self.signature = sign
