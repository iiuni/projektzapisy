import logging

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.decorators.http import require_POST

from libs.ajax_messages import AjaxFailureMessage
from apps.offer.preferences.forms import PreferenceFormset, PreferenceForm
from apps.offer.preferences.models import Preference
from apps.users.decorators import employee_required
from apps.enrollment.courses.models.semester import Semester

logger = logging.getLogger()


@employee_required
def view(request):
    employee = request.user.employee
    Preference.make_preferences(employee)
    prefs = Preference.for_employee(employee)

    formset = PreferenceFormset(queryset=prefs)
    semester = Semester.get_current_semester()

    return render(request, 'offer/preferences/base.html', locals())


@employee_required
@require_POST
def save(request):

    id = request.POST.get('prefid', None)
    if not id:
        return AjaxFailureMessage('InvalidRequest', 'Niepoprawny identyfikator')

    id = int(id)

    try:
        pref = Preference.objects.get(id=id)
    except ObjectDoesNotExist:
        return AjaxFailureMessage('InvalidRequest', 'Podany obiekt nie istnieje')

    if not pref.employee == request.user.employee:
        return AjaxFailureMessage('InvalidRequest', 'Nie możesz edytować nie swoich preferencji')

    form = PreferenceForm(data=request.POST, instance=pref)
    if form.is_valid:
        available_fields = [field.name for field in Preference._meta.get_fields()]
        changed_fields = set(available_fields) & set(request.POST.keys())
        for field in changed_fields:
            try:
                new_value = int(form[field].value())
            except ValueError:
                # We got an empty string - previously made choice has been taken back
                new_value = None
            setattr(pref, field, new_value)
        pref.save()
        form = PreferenceForm(instance=pref)
        return render(request, 'offer/preferences/form_row.html', {'form': form})
    return AjaxFailureMessage('InvalidRequest', 'Coś poszło źle')
