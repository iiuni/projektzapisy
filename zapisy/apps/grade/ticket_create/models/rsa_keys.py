import json
from django.db import models
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from apps.grade.poll.models import Poll


class RSAKeys(models.Model):
    poll = models.OneToOneField('poll.Poll',
                                verbose_name='ankieta',
                                on_delete=models.CASCADE)
    private_key = models.TextField(verbose_name='klucz prywatny')
    public_key = models.TextField(verbose_name='klucz publiczny')

    class Meta:
        verbose_name = 'klucze RSA'
        verbose_name_plural = 'klucze RSA'
        app_label = 'ticket_create'

    def __str__(self):
        return f'Klucze RSA: {self.poll}'

    def serialize_for_signing_protocol(self):
        """Extracts public parts of the key,
        needed for ticket signing protocol"""
        key = RSA.importKey(self.private_key)
        return {
            'n': str(key.n),
            'e': str(key.e),
        }

    @staticmethod
    def parse_raw_tickets(raw_tickets):
        """Parses raw json containing tickets.
        Raises:
            JSONDecodeError: when provided string is not in json format.
            ValueError: when there is something wrong with internal ticket format,
                for example, some of the required fields are not provided, type
                of field is incorrect, there are duplicate ids, or id does not
                exist in database.
        Returns:
            Tuple of (valid_polls, error_polls), where error_polls are list of those
            polls, for which signature was incorrect, and valid_polls is list of named tuples,
            containing two fields, ticket_id and poll, where ticket_id can be used to
            track which ticket has already been used to vote.
        """
        tickets = json.loads(raw_tickets)
        try:
            tickets_list = tickets['tickets']
            tickets_ids = [ticket['id'] for ticket in tickets_list]
        except KeyError as e:
            # If one of the keys wasn't there, it must have been an issue with the format.
            raise ValueError(f"W słowniku brakuje pola {e}")
        except TypeError as e:
            raise ValueError(f"{e}")

        # Make sure there are no duplicate ids
        if len(tickets_ids) != len(set(tickets_ids)):
            raise ValueError("Duplicate ids detected")

        polls = Poll.objects.filter(pk__in=tickets_ids).select_related('rsakeys').order_by('pk')
        # Make sure all provided ids exist in database
        if len(polls) != len(tickets_list):
            raise ValueError("Provided id doesn't exist in database")
        try:
            tickets_list.sort(key=lambda ticket: ticket['id'])
        except KeyError as e:
            raise ValueError(f"W słowniku brakuje pola {e}")

        valid_polls = []
        error_polls = []

        for poll, tickets in zip(polls, tickets_list):
            keys = RSAKeys.objects.get(poll=poll)
            try:
                ticket = int(tickets['ticket'].encode())
                signed_ticket = int(tickets['signature'].encode())
                if keys.verify_ticket(signed_ticket, ticket):
                    valid_polls.append((tickets['ticket'], poll))
                else:
                    error_polls.append(poll)
            except KeyError as e:
                raise ValueError(f"W słowniku brakuje pola {e}")
            except TypeError as e:
                raise ValueError(f"{e}")
        return valid_polls, error_polls

    def sign_ticket(self, ticket):
        ticket = int(ticket.encode())
        key = RSA.importKey(self.private_key)
        if ticket >= key.n or ticket <= 0:
            raise ValueError("Ticket value not in valid range")
        signed = pow(ticket, key.d, key.n)
        return signed

    def verify_ticket(self, signed_ticket, ticket):
        pk = RSA.importKey(self.private_key)
        signature_pow_e = pow(signed_ticket, pk.e, pk.n)
        ticket_hash = SHA256.new(str(ticket).encode()).hexdigest()
        ticket_hash_as_int = int(ticket_hash, 16)

        return ticket_hash_as_int == signature_pow_e
