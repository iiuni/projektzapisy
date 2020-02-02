#!/usr/bin/env python
import argparse
import hashlib
import json
import math
import secrets
import sys
from getpass import getpass
from typing import Dict, NamedTuple, Tuple

import requests


def _hash(m: int) -> int:
    """We are using hash function to disable multiplicative properties
    of RSA encryption/decryption. In other words, if E(m) is standard rsa
    encryption/decryption, then E(m*k) = E(m) * E(k), but if we set
    E'(m) = E(H(m)), where H is hash function, then E'(m*k) != E'(m) * E'(k).
    If we didn't use that, you would be able to generate many tickets, just
    by knowing factors of m. Server will also compute SHA256 of a ticket, so
    if we didn't do this, out ticket would be invalid
    """
    h = hashlib.sha256()
    h.update(str(m).encode())
    return int(h.hexdigest(), 16)


def _inverse(a: int, m: int) -> int:
    """Returns a**(-1) mod m.

    Raises:
        ZeroDivisionError if the inverse does not exist.
    """
    def egcd(a, b) -> Tuple[int, int, int]:
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    g, x, y = egcd(a, m)
    if g != 1:
        raise ZeroDivisionError
    else:
        return x % m


def blind(pub_key, m, r):
    return (m * pow(r, pub_key.e, pub_key.n)) % pub_key.n


def unblind(pub_key, m, r):
    return (m * _inverse(r, pub_key.n)) % pub_key.n


class Ticket:
    """Class which is responsible for generating and holding ticket data."""
    def __init__(self, pub_key):
        # This while loop could be omitted, since condition GCD(r, pub_key.n) !=
        # 1 will probably never happen in our universe lifetime, but lets do
        # that for the sake of correctness.
        while True:
            m = secrets.randbelow(pub_key.n)
            r = secrets.randbelow(pub_key.n)
            if math.gcd(r, pub_key.n) == 1:
                break
        self.m = m
        self.r = r


class RSAPublicKey(NamedTuple):
    n: int
    e: int


class PollData:
    """This class serves the purpose of holding data related to poll"""
    def __init__(self, poll: Dict, ticket=None):
        self.pub_key = RSAPublicKey(int(poll['key']['n']), int(poll['key']['e']))
        self.name = poll['poll_info']['name']
        self.type = poll['poll_info']['type']
        self.id = poll['poll_info']['id']
        self.ticket = ticket

    def serialize_blinded_ticket(self) -> Dict:
        assert self.ticket is not None
        ticket_to_sign = blind(self.pub_key, _hash(self.ticket.m), self.ticket.r)
        return {
            'ticket': str(ticket_to_sign),
            'id': self.id,
        }


class TicketCreate:
    """Main logic."""
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def _post(self, path: str, data=None, json=None) -> requests.Response:
        """Wrapper for self.client.post."""
        def raise_for_status_with_message(r: requests.Response):
            """Takes a "requests" response object and expands the
            raise_for_status method to return more helpful errors.
            """
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if r.text:
                    raise requests.exceptions.HTTPError(f"{e} Error Message: {r.text}")
                else:
                    raise e
            return

        headers = {
            'X-CSRFToken': self.csrf_token,
        }
        r = self.session.post(requests.compat.urljoin(self.url, path),
                              data=data,
                              headers=headers,
                              json=json)
        raise_for_status_with_message(r)
        return r

    def login(self) -> None:
        self.session.get(self.url)
        username = input('Username: ')
        password = getpass('Password: ')
        data = {
            'username': username,
            'password': password,
        }

        r = self._post('/users/login/?next=/grade', data=data)
        # When login is successful Django redirects us where we want.
        if not r.url.endswith('/grade/'):
            raise RuntimeError("Login failed - probably wrong username or password")

    def get_polls(self) -> Dict[int, PollData]:
        """First step of the protocol, query the server for polls metadata(name, type, id)
        and public keys.
        Returns:
            Dict with id as a key, and as a value, data received from the server,
            wrapped in PollData class.
        """
        res = self._post('/grade/ticket/get-poll-data')
        polls = res.json()
        return {poll['poll_info']['id']: PollData(poll) for poll in polls}

    def get_blinded_tickets_for_signing(self, polls: Dict[int, PollData]):
        """Second step of the protocol, after generating tickets, sends them,
        blinded, to the server for signing.
        """
        data = {
            'signing_requests': []
        }

        for poll_data in polls.values():
            ticket = Ticket(poll_data.pub_key)
            poll_data.ticket = ticket
            signing_request = poll_data.serialize_blinded_ticket()
            data['signing_requests'].append(signing_request)
        return data

    def get_tickets(self):
        """Main function."""
        self.login()
        polls = self.get_polls()
        signing_request = self.get_blinded_tickets_for_signing(polls)
        res = self._post('/grade/ticket/sign-tickets', json=signing_request).json()
        tickets_for_user = {
            'tickets': []
        }
        # res is an array of dictionaries with following format:
        # {
        #   id: int
        #   signature: string
        # }
        for signed_ticket in res:
            poll_data = polls[signed_ticket['id']]
            unblinded_signature = unblind(poll_data.pub_key, int(signed_ticket['signature']),
                                          poll_data.ticket.r)
            tickets_for_user['tickets'].append({
                'name': poll_data.name,
                'type': poll_data.type,
                'id': poll_data.id,
                'ticket': str(poll_data.ticket.m),
                'signature': str(unblinded_signature),
            })
        return tickets_for_user

    @property
    def csrf_token(self):
        """get CSRF Token"""
        if 'csrftoken' in self.session.cookies:
            return self.session.cookies['csrftoken']
        raise AttributeError("CSRF token not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='Path to the output file.')
    parser.add_argument('-u', '--url', type=str, default='https://zapisy.ii.uni.wroc.pl/')
    args = parser.parse_args()

    tickets_creator = TicketCreate(args.url)
    tickets = tickets_creator.get_tickets()

    f = sys.stdout if args.filename is None else open(args.filename, 'w')
    f.write(json.dumps(tickets, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
