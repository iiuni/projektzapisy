from typing import Dict

from apps.notifications.exceptions import DescriptionArgumentMissingException
from apps.notifications.templates import mapping


def render_description(description_id: str, description_args: Dict):
    try:
        return mapping[description_id].format(**description_args)
    except KeyError:
        raise DescriptionArgumentMissingException
