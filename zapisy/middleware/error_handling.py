# -*- coding: utf-8 -*-
import traceback
from logging import getLogger

from django.http import HttpResponseNotAllowed
from django.template import loader
from django.utils.deprecation import MiddlewareMixin

logger = getLogger()


# klasa zajmująca się błędami aplikacji
class ErrorHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        # logowanie nie przechwyconych wyjątków
        #
        # jeżeli będzie potrzeba pobrania dokładniejszych informacji o wyjątku:
        # sys.exc_info()
        # traceback.print_tb()
        tb_text = traceback.format_exc()
        logger.exception(tb_text)

    def process_response(self, request, response):
        # obsługiwanie niestandardowych stron błędów
        if isinstance(response, HttpResponseNotAllowed):
            response.content = loader.render_to_string("405.html", {}, request)
        return response
