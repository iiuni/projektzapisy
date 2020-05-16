from django import template
from django.utils import html, safestring
from webpack_loader import utils as webpack_utils

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


@register.simple_tag(name='markdown', takes_context=True)
def markdown_text(context, text, autoescape=True):
    """This renders Markdown string as HTML.

    To render text as markdown put {% markdown text %} into the template. It
    will include JS asset ('common-render-markdown' bundle) on the first use in
    the template, but not on subsequent uses.
    """
    includes = ''
    if 'render_markdown_src' not in context:
        # The first markdown in the template - include JS.
        context['render_markdown_src'] = True
        # Ask Webpack for the location of the asset.
        includes = '\n'.join(webpack_utils.get_as_tags('common-render-markdown'))
    result_html = html.format_html(
        '<span class="markdown">{}</span>{}',
        text,
        safestring.mark_safe(includes),
    )
    return result_html
