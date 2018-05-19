# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA
from apps.enrollment.courses.models import Semester
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import PublicKey, PrivateKey, UsedTicketStamp

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


def check_poll_visiblity(user, poll):
    """
    Checks, whether user is a student entitled to the poll.
    """
    return poll.is_student_entitled_to_poll(user.student)


def check_ticket_not_signed(user, poll):
    """
    Checks, if the user is a student with a yet unused ticket for the poll.
    """
    u = UsedTicketStamp.objects.filter(student=user.student, poll=poll)
    return True if u else False


def mark_poll_used(user, poll):
    """Saves the user's stamp for the poll.

    :raises:
        Student.DoesNotExist: If the user in question is not a student.
    """
    u = UsedTicketStamp(student=user.student,
                        poll=poll)
    u.save()


"""
Ponizsze funkcje implementuja protokol slepych podpisow
"""


def blind_ticket(ticket, pub_key, k):
    """
        Zaślepia kupon przy pomocy podanej przez użytkownika liczby k oraz klucza publicznego
    :param ticket: kupon do zaślepienia
    :param pub_key: klucz publiczny RSA
    :param k: liczba od użytkownika
    :return: Zaślepiony podpis kuponu
    """
    return pub_key.blind(ticket, k)


def sign_ticket(ticket, priv_key):
    """
        Podpisuje kupon kluczem prywatnym
    :param ticket: kupon do podpisu
    :param priv_key: prywatny klucz RSA
    :return: podpisany kupon
    """
    priv = RSA.importKey(priv_key.private_key)
    return priv.sign(ticket, 0)[0]


def unblind_ticket(ticket, priv_key, k):
    """
        Odkrywa kupon przy pomocy klucza prywatnego oraz liczby k podanej przez użytkownika
    :param ticket: kupon do odkrycia
    :param priv_key: prywatny klucz RSA
    :param k: liczba podana przez użytkownika
    :return: uzyskany po odkryciu podpis ślepego kuponu
    """
    return priv_key.unblind(ticket, k)


def verify_ticket(ticket, signature, priv_key):
    """
        Weryfikuje przy pomocy podanego klucza prywatnego, czy kupon jest zgodny z podaną sygnaturą
    :param ticket:
    :param signature: podpis ślepego kuponu
    :param priv_key: prywatny klucz RSA
    :return:
    """
    return priv_key.verify(ticket, (signature,))


def convert_ticket_record(ticket):
    """
    Konwertuje rekord postaci:
        poll_id: XYZ
        TICKET
    do pary (poll_id, TICKET)
    :param ticket: kupon do konwersji
    :return: wynik konwersji
    """
    t = ticket.strip().split('\r\n')
    if len(t) > 1:
        poll_id = str(t[0]).strip().split('poll_id:')[1]
        return int(poll_id), str(t[1]).strip()


class Signature:
    """
        Pomocnicza klasa, służy jako model dla widoku signed_tickets.html
    """

    def __init__(self, poll_id, sign):
        self.poll_id = poll_id
        self.signature = sign
