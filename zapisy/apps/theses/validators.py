"""Custom Django admin validators for theses system-related admin pages"""
from typing import Optional

from django.core.exceptions import ValidationError

from apps.users.models import Employee
from .users import get_num_board_members, is_theses_board_member


def validate_num_required_votes(value: int):
    """Validate that the number of required "accepted" votes
    is in range, that is, not negative and not more than the number
    of theses board members."""
    max_value = get_num_board_members()
    if not 1 <= value <= max_value:
        raise ValidationError(
            "Liczba wymaganych głosów musi być z przedziału "
            f'[1, {max_value} (liczba członków komisji)]'
        )


def validate_master_rejecter(value: Optional[int]):
    if value is not None:
        try:
            person = Employee.objects.get(pk=value)
            if not is_theses_board_member(person):
                raise ValidationError(
                    f'{person} nie jest członkiem komisji prac dyplomowych. Skład komisji ' +
                    "definiować można w zakładce Użytkownicy -> Grupy -> Komisja prac dyplomowych."
                )
        except Employee.DoesNotExist:
            # This is unexpected - users generally shouldn't be able to do that,
            # short of manually crafting malicious requests
            raise ValidationError("Podano niepoprawnego pracownika")
