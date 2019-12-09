from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from apps.users.roles import Roles


def student_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is student, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        Roles.is_student,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def employee_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is employee, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        Roles.is_employee,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def external_contractor_forbidden(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Check whether the logged user is either a student or an actual employee
    (i.e. not external contractor).
    Redirect to the login page if that's not the case.
    """

    decorator = user_passes_test(
        lambda u: not Roles.is_external_contractor(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name)

    if view_func:
        return decorator(view_func)

    return decorator
