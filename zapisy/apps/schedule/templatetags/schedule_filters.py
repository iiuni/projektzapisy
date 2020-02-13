"""Template Tags useful in schedule views."""
from django import template

register = template.Library()


@register.filter(is_safe=True)
def number_to_weekday(value: int):
    """Translates a number into a weekday."""
    types_dict = {
        1: "pn",
        2: "wt",
        3: "śr",
        4: "cz",
        5: "pt",
        6: "so",
        7: "ni",
    }
    return types_dict.get(value, "")
