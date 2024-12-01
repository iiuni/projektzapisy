import logging
from typing import List

import redis
import rollbar.contrib.django.middleware

from apps.common.redis import flush_by_pattern

TIMEOUT = 3600
KEY_PREFIX = '404:'
KEY_PATTERN = KEY_PREFIX + '*'


class RollbarOnly404Limited:
    """Throttles the number of the 404 reports sent to Rollbar originating from the same user.

    The clients are identified using their IP addresses and this data is temporarily stored
    in Redis. The constant TIMEOUT contains the length of a timeframe (in seconds), during which
    a client may cause a report to be sent. Sending more requests during this period does not
    prolong it; only the time of the last request passed to Rollbar is used. This class does not
    communicate with the Rollbar's servers. Any first request from a client in a timeframe will be
    simply passed to the official middleware provided by the Rollbar project. In any case, the user
    will see the error page and their client should receive 404 error code. Any action
    performed by this middleware should not be deduced by a client.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rollbar_404 = rollbar.contrib.django.middleware.RollbarNotifierMiddlewareOnly404(get_response)
        self.redis_client = redis.Redis()
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404:
            return response
        ip = self.request_to_ip(request)
        if not self.check_and_add(ip):
            self.logger.info(f'Added {ip} to the ignored 404 list. '
                             f'Currently it contains {len(self.list_ignored())} entries')
            return self.rollbar_404.process_response(request=request, response=response)
        return response

    def list_ignored(self) -> List[str]:
        return [key[len(KEY_PREFIX):] for key in self.redis_client.keys(KEY_PATTERN)]

    def flush(self) -> None:
        flush_by_pattern(self.redis_client, KEY_PATTERN)

    @staticmethod
    def ip_to_key(ip: str) -> str:
        return KEY_PREFIX + ip

    @staticmethod
    def request_to_ip(request) -> str:
        return request.META.get("REMOTE_ADDR")

    def check_and_add(self, ip: str) -> bool:
        """This function checks whether a key was present and adds it for a set time if it was not.

        As the timeout may only be set for a key and not for a value in an array, we use
        the individual entries with empty values for each IP address. SET returns None, if the key
        was not present. In such case, no value is set.
        """
        key = self.ip_to_key(ip)
        return self.redis_client.set(name=key, value="", ex=TIMEOUT, nx=True) is None
