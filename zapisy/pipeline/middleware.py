from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.html import strip_spaces_between_tags as minify_html
from django.utils.deprecation import MiddlewareMixin


class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Originally the code did not check whether the header was present;
        # the assumption was that every HTTP request would include it
        # This is not necessarily the case as certain requests naturally don't
        # carry a payload, such as DELETE; this failed in those cases
        if 'Content-Type' in response and 'text/html' in response['Content-Type']:
            try:
                response.content = minify_html(response.content.strip())
            except DjangoUnicodeDecodeError:
                pass
        return response
