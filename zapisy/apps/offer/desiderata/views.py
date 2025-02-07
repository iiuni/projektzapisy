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
        hours_valid = hours_formset.is_valid()
        comments_valid = comments_form.is_valid()
        if hours_valid() and comments_valid:
            hours_formset.save(desiderata, employee)
            comments_form.save()
            desiderata = Desiderata.get_desiderata(employee)
            desiderata_formset_initial = Desiderata.get_desiderata_to_formset(desiderata)
            messages.success(request, 'Zmiany zapisano pomyślnie')
        else:
            error_messages = []
            if not hours_valid:
                error_messages.append(hours_formset.errors.as_text())
            if not comments_valid:
                error_messages.append(comments_form.errors.as_text())
            messages.error(request, 'Formularz zawiera błędy: ' + ' '.join(error_messages))

    hours_formset = DesiderataFormSet(initial=desiderata_formset_initial)
    data = {
        'hours_formset': hours_formset,
        'comments_form': comments_form,
    }
    return render(request, 'desiderata/change_desiderata.html', data)
