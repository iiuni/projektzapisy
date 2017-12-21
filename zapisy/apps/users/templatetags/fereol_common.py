# -*- coding: utf-8 -*-
import math

from django import template
from django.utils.safestring  import mark_safe
import postmarkup
import logging

register = template.Library()
logger = logging.getLogger()

@register.filter
def bbcode(str):
    markup = postmarkup.PostMarkup()

    markup.add_tag(postmarkup.SimpleTag, 'b', 'strong')
    markup.add_tag(postmarkup.SimpleTag, 'i', 'em')
    markup.add_tag(postmarkup.SimpleTag, 'u', 'u')
    markup.add_tag(postmarkup.SimpleTag, 's', 's')

    return markup.render_to_html(str)

@register.filter
def nl2br(str):
    return str.replace("\n", "<br />")

# filter checks url validity, and:
# - if it's ok (modulo "http://" prefix) - returns it
# - in the other case - returns "/" and logs it
@register.filter
def validate_url(str):
    from django.core.validators import URLValidator, ValidationError
    from io import StringIO
    import traceback
    import string
    validate = URLValidator()
    try:
        validate(str)
    except ValidationError:
        try:
            validate('http://' + str)
            str = 'http://' + str
        except ValidationError:
            trace = StringIO()
            traceback.print_stack(file=trace)
            trace = trace.getvalue().split('\n')
            trace = [str for str in trace if str.find('html') >= 0]
            trace = string.join(trace, '\n')
            logger.warning('Invalid URL couldn\'t be displayed in template: '
                    + str + '\n' + trace)
            return '/'
    return str

@register.tag(name='captureas')
def do_captureas(parser, token):
    '''
        Dumps its contents into a context variable.

        Parameter: variable name

        Example use:
        {% captureas examplevar %}{% url 'exampleurl' %}{% endcaptureas %}
        URL: {{ examplevar }}

        Source: http://djangosnippets.org/snippets/545/
    '''
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)

class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''

@register.filter
def safestring( str ):
    return mark_safe( str )

@register.filter
def timedelta(delta):
    if delta.days < 0:
        raise RuntimeError('Nie obsługiwany parametr')
    if delta.days > 1:
        return 'za ' + str(delta.days) + ' dni'
    seconds = delta.days * 24 * 3600 + delta.seconds
    if seconds > 3600:
        hours = int(math.floor(seconds / 3600.0 + 0.5))
        if hours == 1:
            return 'za godzinę'
        if hours >= 10 and hours <= 20:
            return 'za ' + str(hours) + ' godzin'
        if hours % 10 >= 2 and hours % 10 <= 4:
            return 'za ' + str(hours) + ' godziny'
        return 'za ' + str(hours) + ' godzin'
    if seconds > 60:
        minutes = int(math.floor(seconds / 60.0 + 0.5))
        if minutes == 1:
            return 'za minutę'
        if minutes >= 10 and minutes <= 20:
            return 'za ' + str(minutes) + ' minut'
        if minutes % 10 >= 2 and minutes % 10 <= 4:
            return 'za ' + str(minutes) + ' minuty'
        return 'za ' + str(minutes) + ' minut'
    return 'za mniej niż minutę'

@register.filter
def hash(map, key):
    if not map:
        return None
    if key in map:
        return map[key]
    else:
        return None

@register.filter
def getattribute(object, attribute):
    return getattr(object, attribute)
