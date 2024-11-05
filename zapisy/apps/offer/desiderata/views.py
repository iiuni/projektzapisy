from django.contrib import messages
from django.shortcuts import render

from apps.offer.desiderata.forms import DesiderataFormSet, DesiderataOtherForm
from apps.offer.desiderata.models import Desiderata, DesiderataOther
from apps.users.decorators import employee_required


@employee_required
def change_desiderata(request):
    """Handles form in semester with desiderata currently open."""
    user = request.user
    employee = user.employee

    desiderata = Desiderata.get_desiderata(employee)
    other, _ = DesiderataOther.objects.get_or_create(employee=employee)
    desiderata_formset_initial = Desiderata.get_desiderata_to_formset(desiderata)

    if request.method == 'POST':
        hours_formset = DesiderataFormSet(request.POST)
        comments_form = DesiderataOtherForm(request.POST, instance=other)
        if hours_formset.is_valid() and comments_form.is_valid():
            hours_formset.save(desiderata, employee)
            comments_form.save()
            
            desiderata = Desiderata.get_desiderata(employee)
            desiderata_formset_initial = Desiderata.get_desiderata_to_formset(desiderata)
            
            messages.success(request, 'Zmiany zapisano pomyślnie')
        else:
            messages.error(request, 'Nie udało się zapisać zmian. Proszę poprawić błędy w formularzu.')
    else:
        comments_form = DesiderataOtherForm(instance=other)
    hours_formset = DesiderataFormSet(initial=desiderata_formset_initial)
    data = {
        'hours_formset': hours_formset,
        'comments_form': comments_form,
    }
    return render(request, 'desiderata/change_desiderata.html', data)
