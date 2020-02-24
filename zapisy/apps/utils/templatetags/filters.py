from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def add_class(field, class_name):
    return field.as_widget(attrs={"class": " ".join([field.css_classes(), class_name])})


@register.filter(name="lookup")
def lookup(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    return None


@register.filter(name="next")
def next_iterator(iterator):
    return next(iterator)


@register.filter(name="max")
def maximum(first, second):
    if isinstance(first, str):
        first = type(second)(first)
    return max(first, second)


@register.filter(name="min")
def minimum(first, second):
    if isinstance(first, str):
        first = type(second)(first)
    return min(first, second)


@register.filter(name='markdown', needs_autosecape=True)
def markdown_text(text, autoescape=True):
    """This renders Markdown string as HTML.

    For the markdown string to be rendered you need to include 'render-markdown'
    bundle in the template.
    """
    if autoescape:
        esc = conditional_escape
    else:
        def esc(x):
            return x
    result_html = '<span class="markdown">%s</span>' % esc(text)
    return mark_safe(result_html)
