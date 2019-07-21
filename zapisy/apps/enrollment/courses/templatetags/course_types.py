"""Template Tags useful in courses views."""
from django import template

register = template.Library()


@register.filter(is_safe=True)
def decode_class_type_plural(value: str):
    """Translates a class type enum into plural form of a Polish word."""
    types_dict = {
        '1': "Wykłady",
        '2': "Ćwiczenia",
        '3': "Pracownie",
        '4': "Ćwiczenia (poziom zaawansowany)",
        '5': "Ćwiczenio-pracownie",
        '6': "Seminaria",
        '7': "Lektoraty",
        '8': "Zajęcia sportowe",
        '9': "Repetytoria",
        '10': "Projekty",
        '11': "Tutoring",
        '12': "Proseminaria",
    }
    return types_dict.get(value, "")


@register.filter(is_safe=True)
def decode_class_type_singular(value: str):
    """Translates a class type enum into singular form of a Polish word."""
    types_dict = {
        '1': "Wykład",
        '2': "Ćwiczenia",
        '3': "Pracownia",
        '4': "Ćwiczenia (poziom zaawansowany)",
        '5': "Ćwiczenio-pracownia",
        '6': "Seminarium",
        '7': "Lektorat",
        '8': "Zajęcia sportowe",
        '9': "Repetytorium",
        '10': "Projekt",
        '11': "Tutoring",
        '12': "Proseminarium",
    }
    return types_dict.get(value, "")
