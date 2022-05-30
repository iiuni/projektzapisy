import logging
from typing import List

import redis
import rollbar.contrib.django.middleware

TIMEOUT = 3600
KEY_PREFIX = '404:'
KEY_PATTERN = KEY_PREFIX + '*'


class RollbarOnly404Limited:
    """ Ogranicza liczbę zgłoszeń 404 wysyłanych do Rollbara pochodzących od tych samych klientów.

    * Klienci są identyfikowani przy użyciu adresów IP, a dane o nich są przechowywane w Redisie
    (z założenia nietrwale).
    * Zmienna TIMEOUT określa (w sekundach) jak często dany klient może spowodować wygenerowanie
    zgłoszenia. Wysłanie kolejnych nieudanych zapytań w okresie ignorowania nie wydłuża czasu -
    - liczy się moment ostatniego zapytania z wysłanym zgłoszeniem.
    * Ta klasa nie obsługuje w żaden sposób komunikacji z Rollbarem. Zgłoszenia są wysyłane
    za pośrednictwem standardowego middleware'u od twórców projektu.
    * Klient za każdym razem zobaczy stronę błędu i otrzyma kod 404, więc działanie tego modułu
    jest z jego punktu widzenia przezroczyste.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rollbar_404 = rollbar.contrib.django.middleware.RollbarNotifierMiddlewareOnly404()
        self.redis_client = redis.Redis()
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404:
            return response
        ip = self.request_to_ip(request)
        if not self.check_and_add(ip):
            self.logger.info(f'Added {ip} to the ignored 404 list. Currently it contains {self.list_ignored()}')
            return self.rollbar_404.process_response(request=request, response=response)
        return response

    def list_ignored(self) -> List[str]:
        return [key[len(KEY_PREFIX):] for key in self.redis_client.keys(KEY_PATTERN)]

    def flush(self) -> None:
        for key in self.redis_client.scan_iter(KEY_PATTERN):
            self.redis_client.delete(key)

    @staticmethod
    def ip_to_key(ip: str) -> str:
        return KEY_PREFIX + ip

    @staticmethod
    def request_to_ip(request) -> str:
        return request.META.get("REMOTE_ADDR")

    def check_and_add(self, ip: str) -> bool:
        key = self.ip_to_key(ip)
        return self.redis_client.set(name=key, value="", ex=TIMEOUT, nx=True) is None
