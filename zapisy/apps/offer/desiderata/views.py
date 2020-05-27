from django.contrib import messages
from django.shortcuts import render

from apps.enrollment.courses.models.semester import Semester
from apps.offer.desiderata.forms import DesiderataFormSet, DesiderataOtherForm
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.users.decorators import employee_required


@employee_required
def change_desiderata(request):
    """Handles form in semester with desiderata currently open."""
    user = request.user
    employee = user.employee
    semester = Semester.get_default_semester()

    desiderata = Desiderata.get_desiderata(employee, semester)
    other = DesiderataOther.get_desiderata_other(employee, semester)
    desiderata_formset_initial = Desiderata.get_desiderata_to_formset(desiderata)

    if request.method == 'POST':
        formset = DesiderataFormSet(request.POST)
        other_form = DesiderataOtherForm(request.POST, instance=other)
        if formset.is_valid():
            formset.save(desiderata, employee, semester)
            desiderata = Desiderata.get_desiderata(employee, semester)
            desiderata_formset_initial = Desiderata.get_desiderata_to_formset(desiderata)
        if other_form.is_valid():
            other_form.save()
        messages.success(request, 'Zmiany zapisano pomyślnie')
    else:
        other_form = DesiderataOtherForm(instance=other)
    formset = DesiderataFormSet(initial=desiderata_formset_initial)
    data = {
        'formset': formset,
        'other_form': other_form,
        'semester': semester
    }
    return render(request, 'offer/desiderata/change_desiderata.html', data)
