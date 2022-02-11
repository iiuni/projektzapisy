from typing import Dict

from apps.notifications.exceptions import DescriptionArgumentMissingException
from apps.notifications.exceptions import TitleArgumentMissingException
from apps.notifications.templates import mapping
from apps.notifications.templates import mapping_title


def render_description(description_id: str, description_args: Dict):
    try:
        return mapping[description_id].format(**description_args)
    except KeyError:
        raise DescriptionArgumentMissingException


def render_title(title_id: str, title_args: Dict):
    try:
        return mapping_title[title_id].format(**title_args)
    except KeyError:
        raise TitleArgumentMissingException
