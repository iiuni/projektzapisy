from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.html import strip_spaces_between_tags as minify_html
from django.utils.deprecation import MiddlewareMixin

class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            try:
                response.content = minify_html(response.content.strip())
            except DjangoUnicodeDecodeError:
                pass
        return response
