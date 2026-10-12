from typing import Dict, Any

from django.http import JsonResponse
from django.template import engines, Template


def render_templates_json(context: Dict[str, Any], templates: Dict[str, Template],
                          html_strings: Dict[str, str]) -> JsonResponse:
    """Parses strings into django templates and renders them.

    Templates arguments are expected as (HTML id: Template).
    Html_strings arguments are expected as (HTML id: HTML code).
    Returns JSON response with mappings HTML id: HTML-correct string.
    """,
    engine = engines['django']
    templates.update({id: engine.from_string(string) for id, string in html_strings.items()})
    response = {id: template.render(context) for id, template in templates.items()}
    return JsonResponse(response)
