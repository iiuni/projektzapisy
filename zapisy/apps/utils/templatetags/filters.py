from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def add_class(field, class_name):
    return field.as_widget(
        attrs={"class": " ".join([field.css_classes(), class_name])})


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
