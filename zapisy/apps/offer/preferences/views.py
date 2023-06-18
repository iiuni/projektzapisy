from django.contrib import messages
from django.shortcuts import render

from apps.users.decorators import employee_required

from .forms import prepare_formset


@employee_required
def main(request):
    employee = request.user.employee

    if request.method == 'POST':
        formset = prepare_formset(employee, post=request.POST)
        if formset.is_valid():
            formset.save()
            messages.info(request, "Zapisano głos.")
        else:
            # note: this is a temporary diagnostic message.
            messages.error(request, "A validation error has occured - please reload the app.")
    else:
        formset = prepare_formset(employee)
        messages.info(request, formset.initial_form_count())

    return render(request, 'preferences/main.html', {
        'formset': formset,
    })
