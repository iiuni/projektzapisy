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
        formset = prepare_formset(employee)

    return render(request, 'preferences/main.html', {
        'formset': formset,
    })
