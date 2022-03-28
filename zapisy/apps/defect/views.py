from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from gdstorage.storage import GoogleDriveStorage

from apps.notifications.custom_signals import defect_modified
from .forms import DefectForm, Image, DefectImageFormSet, ExtraImagesNumber, InformationFromRepairerForm
from .models import Defect, StateChoices, DefectMaintainer
from ..users.decorators import employee_required

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()


@employee_required
def index(request):
    is_repairer_val = is_repairer(request.user.id)
    if request.method == "POST":
        query = request.POST
        if_empty, defects_list = parse_names(request)
        if (query.get('print') is None and not (if_empty is False)) or len(defects_list) == 0:
            messages.error(request, "Akcja wymaga zaznaczenia elementów")
        elif query.get('print') is not None:
            if defects_list is None or len(defects_list) == 0:
                return print_defects(request)
            return print_defects(request, Defect.objects.filter(pk__in=defects_list))
        elif query.get('done') is not None:
            if is_repairer_val:
                Defect.objects.filter(pk__in=defects_list).update(state=StateChoices.DONE)
            else:
                messages.error(request,
                               "Stan może zostać zmieniony tylko przez osoby do tego wyznaczone")
        elif query.get('delete') is not None:
            if is_repairer_val:
                to_delete = Defect.objects.filter(pk__in=defects_list)

                images_to_delete = []
                for defect in to_delete:
                    for image in defect.image_set.all():
                        images_to_delete.append(image.image.name)

                query_set = ", ".join(map(lambda x: x['name'], list(to_delete.values())))
                messages.info(request, "Usunięto następujące usterki: " + query_set)
                to_delete.delete()

                for image_name in images_to_delete:
                    image_path = '/zapisy/defect/' + image_name
                    if gd_storage.exists(image_path):
                        gd_storage.delete(image_path)
            else:
                messages.error(request,
                               "Z tego poziomu usterka może zostać usunięta tylko przez osoby do tego wyznaczone")
        else:
            messages.error(request, "Nie wprowadzono metody. Ten błąd nie powinien się zdarzyć. Proszę o kontakt z "
                                    "administratorem systemu zapisów.")
    return render(request, "defectMain.html", {"defects": Defect.objects.all().select_related("reporter"),
                                               "visibleDefects": [parse_defect(defect) for defect in
                                                                  Defect.objects.all().select_related("reporter")],
                                               'is_repairer': is_repairer_val})


def parse_names(request):
    try:
        return int(request.POST.get("if_form_empty")) != 0, \
               list(map(int, request.POST.get("defects_ids").split(';')))
    except Exception:
        return True, []


def parse_defect(defect: Defect):
    return {"id": defect.id, "name": defect.name, "place": defect.place, "status_color": defect.get_status_color(),
            "state": defect.get_state_display(), "state_id": [defect.state],
            "creation_date": defect.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
            "last_modification": defect.last_modification.strftime('%Y-%m-%d %H:%M:%S')}


@employee_required
def show_defect(request, defect_id):
    try:
        defect = Defect.objects.get(pk=defect_id)
        images = Image.objects.filter(defect=defect)
        image_urls = []

        for image in images:
            image_urls.append(image.image.url[:-16])

        info_form = InformationFromRepairerForm(instance=defect)

        return render(request, 'showDefect.html', {'defect': defect, 'image_urls': image_urls, 'info_form': info_form,
                                                   'is_repairer': is_repairer(request.user.id)})
    except Defect.DoesNotExist:
        messages.error(request, "Nie istnieje usterka o podanym id.")
        return redirect('defects:main')


@employee_required
def edit_defect(request, defect_id):
    try:
        defect = Defect.objects.get(pk=defect_id)
        return edit_defect_helper(request, defect)
    except Defect.DoesNotExist:
        messages.error(request, "Nie istnieje usterka o podanym id.")
        return redirect('defects:main')


def edit_defect_helper(request, defect):
    if request.method == 'POST':
        return edit_defect_post_request(request, defect_id=defect.id)
    else:
        form = DefectForm(instance=defect)
        formset = DefectImageFormSet()
        images = []

        for image in Image.objects.filter(defect=defect):
            images.append((image.id, image.image.url[:-16]))
    context = {'form': form, 'formset': formset, "response": request.method, "edit": True, 'images': images,
               'extra_images_number': ExtraImagesNumber, 'defect_id': defect.id}
    return render(request, 'addDefect.html', context)


@employee_required
def add_defect(request):
    """Show form for create new defect."""
    if request.method == 'POST':
        return add_defect_post_request(request)
    else:
        form = DefectForm()
        formset = DefectImageFormSet()
    context = {'form': form, 'formset': formset, "response": request.method, 'extra_images_number': ExtraImagesNumber}
    return render(request, 'addDefect.html', context)


def return_error_and_reload(request, form, edit, errors):
    messages.error(request, errors)
    formset = DefectImageFormSet()
    context = {'form': form, 'formset': formset, "response": request.method,
               'extra_images_number': ExtraImagesNumber, "edit": edit}
    return render(request, 'addDefect.html', context)


def edit_defect_post_request(request, defect_id):
    form = DefectForm(request.POST, request.FILES)
    if not form.is_valid():
        return return_error_and_reload(request, form, True, str(form.errors))

    form_data = form.cleaned_data
    defect = Defect.objects.filter(pk=defect_id)
    formset = DefectImageFormSet(request.POST, request.FILES, instance=defect.get())

    if not formset.is_valid():
        return return_error_and_reload(request, form, True, str(formset.errors))

    defect.update(name=form_data['name'], last_modification=now(),
                  description=form_data['description'], place=form_data['place'])
    formset.save()

    if request.user.id != defect.get().reporter.id:
        defect_modified.send_robust(
            sender=Defect,
            instance=defect.get(),
            user=defect.get().reporter
        )

    messages.success(request, "Edytowano usterkę")
    return redirect('defects:show_defect', defect_id=defect_id)


def add_defect_post_request(request):
    form = DefectForm(request.POST, request.FILES)
    if not form.is_valid():
        return return_error_and_reload(request, form, False, str(form.errors))

    creation_date = now()
    form_data = form.cleaned_data
    defect = Defect(name=form_data['name'], creation_date=creation_date, last_modification=creation_date,
                    place=form_data['place'], description=form_data['description'], reporter=request.user,
                    state=0)

    formset = DefectImageFormSet(request.POST, request.FILES, instance=defect)
    if not formset.is_valid():
        return return_error_and_reload(request, form, False, str(formset.errors))

    defect.save()
    formset.save()

    messages.success(request, "Dodano pomyślnie usterkę")
    return redirect('defects:main')


def print_defects(request, defects_list=None):
    if defects_list is None:
        return render(request, 'defectPrint.html', {'defects': Defect.objects.all()})
    else:
        return render(request, 'defectPrint.html', {'defects': Defect.objects.filter(pk__in=defects_list)})


def delete_image(request, image_id):
    if request.method == "POST":
        image = get_object_or_404(Image, id=image_id)
        defect_id = image.defect.id
        image_path = '/zapisy/defect/' + image.image.name

        image.delete()

        if gd_storage.exists(image_path):
            gd_storage.delete(image_path)

        if request.user.id != image.defect.reporter.id:
            defect_modified.send_robust(
                sender=Defect,
                instance=image.defect,
                user=image.defect.reporter
            )

        messages.success(request, "Pomyślnie usnięto zdjęcie")
        return redirect('defects:edit_defect', defect_id=defect_id)
    raise Http404


def post_information_from_repairer(request, defect_id):
    if request.method == "POST":
        if not is_repairer(request.user.id):
            messages.error(request, "Informacja od serwisanta"
                                    " może zostać wypełniona tylko przez osoby do tego wyznaczone.")
            return redirect('defects:show_defect', defect_id=defect_id)
        info_form = InformationFromRepairerForm(request.POST)
        if not info_form.is_valid():
            messages.error(request, info_form.errors)
            return redirect('defects:show_defect', defect_id=defect_id)

        info_form_data = info_form.cleaned_data
        defect = Defect.objects.filter(pk=defect_id)
        defect.update(information_from_repairer=info_form_data['information_from_repairer'],
                      state=info_form_data["state"])

        if request.user.id != defect.get().reporter.id:
            defect_modified.send_robust(
                sender=Defect,
                instance=defect.get(),
                user=defect.get().reporter
            )

        messages.success(request, "Pomyślnie zmieniono informację od serwisanta")
        return redirect('defects:show_defect', defect_id=defect_id)
    raise Http404


def is_repairer(user_id):
    return DefectMaintainer.objects.filter(user_id=user_id).exists()
