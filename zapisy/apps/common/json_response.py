from typing import Mapping, Any

from django.http import JsonResponse
from django.template import Template


def render_templates_json(context: Mapping[str, Any], templates: Mapping[str, Template]):
    """Renders django template elements from strings.

    Templates arguments are expected as (HTML id: Template).
    Returns JSON response with mappings HTML id: HTML-correct string.
    """,
    response = {id: template.render(context) for id, template in templates.items()}
    return JsonResponse(response)
