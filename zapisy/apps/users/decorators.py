# -*- coding: utf-8 -*-
from functools import update_wrapper

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.utils.http import urlquote

from apps.users.models import Employee, Student


def student_required(function=None, redirect_to=None):
    """
    Decorator that checks that the user has a student profile,
    redirecting to the given or the default login page as needed.
    """

    def test_f(user):
        try:
            sth = user.student
            if sth and sth.status == 0:
                return True
            else:
                return False
        except AttributeError:
            return False
        except Student.DoesNotExist:
            return False
    if function:
        return _CheckProfileOr403(function, test_f, redirect_to)
    return (lambda f: _CheckProfileOr403(f, test_f, redirect_to))

def employee_required(function=None,
                      redirect_to=None):
    """
    Decorator that checks that the user has a student profile,
    redirecting to the given or the default login page as needed.
    """
    def test_f(user):
        try:
            sth = user.employee
            if sth:
                return True
            else:
                return False
        except AttributeError:
            return False
        except Employee.DoesNotExist:
            return False
    if function:
        return _CheckProfileOr403(function, test_f, redirect_to)
    return lambda f: _CheckProfileOr403(f, test_f, redirect_to)

class _CheckProfileOr403(object):
    """
    Class that checks that the user passes the given test,
    redirecting to the given view, login page by default.

    Check django.contrib.auth.decorators._CheckLogin for more info.
    """
    def __init__(self, view_func, test_func, redirect_to=None):
        self.view_func = view_func
        self.test_func = test_func
        self.redirect_to = redirect_to
        # see _CheckLogin
        update_wrapper(self, view_func, updated=())
        for k in view_func.__dict__:
            if k not in self.__dict__:
                self.__dict__[k] = view_func.__dict__[k]

    def __get__(self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return _CheckProfileOr403(view_func, self.test_func, self.redirect_to)

    def __call__(self, request, *args, **kwargs):
        if self.test_func(request.user):
            return self.view_func(request, *args, **kwargs)
        if not self.redirect_to:
            from django.conf import settings
            login_url = settings.LOGIN_URL
            path = urlquote(request.get_full_path())
            tup = login_url, REDIRECT_FIELD_NAME, path
            self.redirect_to = '%s?%s=%s' % tup
        return redirect(self.redirect_to)
