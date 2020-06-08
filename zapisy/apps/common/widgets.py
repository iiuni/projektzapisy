from django.forms import Media, widgets
from webpack_loader import utils as webpack_utils


class MarkdownArea(widgets.Widget):
    """Form widget with live Markdown preview.

    This widget may be used just like any Django widget for any form
    (text)field. It automatically adds its assets (css and js) into the form.
    They must be included in the template:

        {{ form.media }}

    (Crispy will do it for you.)
    """
    template_name = 'widgets/markdown-editor.html'

    @property
    def media(self):
        js_media = webpack_utils.get_files('common-markdown-editor', extension='js')
        css_media = webpack_utils.get_files('common-markdown-editor', extension='css')
        return Media(js=[f['url'] for f in js_media], css={
            'all': [f['url'] for f in css_media],
        })
