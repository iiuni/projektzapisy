from django import template
from django.template import resolve_variable
from django.template import Library, Node, TemplateSyntaxError

register = template.Library()

class TruncateNode(Node):
    def __init__(self, value, cutoff):
        self.value, self.cutoff = value, cutoff

    def render(self, context):
        truncated = template.resolve_variable(self.value, context)
        size = int(template.resolve_variable(self.cutoff, context))
        if len(truncated) > size and size > 3:
            truncated = truncated[0:(size - 3)] + '...'

        return truncated

def truncate(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("truncate takes exactly two arguments, string, size")
    return TruncateNode(bits[1], bits[2])

register.tag('truncate', truncate)
