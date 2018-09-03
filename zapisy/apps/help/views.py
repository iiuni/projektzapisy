from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from apps.users.decorators import employee_required


def main_page(request):
    return render(request, 'help/base.html', {})


def terms(request):
    return render(request, 'help/terms.html', {})


def rules(request):
    return render(request, 'help/rules.html', {})


def enrollment(request):
    return render(request, 'help/enrollment.html', {})


def grade(request):
    return render(request, 'help/grade.html', {})


def mobile(request):
    return render(request, 'help/mobile.html', {})


def export(request):
    return render(request, 'help/export.html', {})


def offer(request):
    return render(request, 'help/offer.html', {})


@staff_member_required
def admin(request):
    return render(request, 'help/admin.html', {})


@employee_required
def employee(request):
    return render(request, 'help/employee.html', {})
