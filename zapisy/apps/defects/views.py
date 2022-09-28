import logging

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from . import models
from .forms import DefectForm, DefectImage, DefectImageFormSet, ExtraImagesNumber, InformationFromDefectManagerForm
from .models import Defect, StateChoices, DefectManager
from ..notifications.custom_signals import defect_modified
from ..users.decorators import employee_required

storage = models.select_storage()


@employee_required
def index(request):
    is_defect_manager_val = is_defect_manager(request.user.id)
    return render(request, "defectsMain.html", {"defects": Defect.objects.all().select_related("reporter"),
                                                "visibleDefects": [parse_defect(defect) for defect in
                                                                   Defect.objects.all().select_related("reporter")],
                                                'is_defect_manager': is_defect_manager_val})


def delete_defects_endpoint(request):
    is_defect_manager_val = is_defect_manager(request.user.id)
    if request.method == "POST":
        defects_list = parse_names(request.POST, "defects_ids")
        if len(defects_list) == 0:
            messages.error(request, "Akcja wymaga zaznaczenia elementów")
            return redirect('defects:main')

        if not is_defect_manager_val:
            messages.error(request,
                           "Z tego poziomu usterka może zostać usunięta tylko przez osoby do tego wyznaczone")
            return redirect('defects:main')

        to_delete = Defect.objects.filter(pk__in=defects_list)
        images_to_delete = []

        for defect in to_delete:
            for image in defect.image_set.all():
                images_to_delete.append(image.image.name)

        query_set = ", ".join(map(lambda x: x['name'], list(to_delete.values())))
        messages.info(request, "Usunięto następujące usterki: " + query_set)

        to_delete.delete()
        delete_images(images_to_delete)
    messages.error(request, "Nieprawidłowa metoda zapytania http.")
    return redirect('defects:main')


def delete_images(images_to_delete):
    for image_name in images_to_delete:
        image_path = settings.GOOGLE_DRIVE_STORAGE_DEFECT_IMAGES_DIR + image_name
        if storage.exists(image_path):
            storage.delete(image_path)


def parse_names(form_fields, field):
    try:
        return list(map(int, form_fields.get(field).split(',')))
    except Exception:
        []


def parse_defect(defect: Defect):
    return {"id": defect.id, "name": defect.name, "place": defect.place, "status_color": defect.get_status_color(),
            "state": defect.get_state_display(), "state_id": [defect.state],
            "reporter": defect.reporter.first_name + " " + defect.reporter.last_name,
            "creation_date": defect.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
            "last_modification": defect.last_modification.strftime('%Y-%m-%d %H:%M:%S')}


@employee_required
def show_defect(request, defect_id):
    try:
        defect = Defect.objects.get(pk=defect_id)
        images = DefectImage.objects.filter(defect=defect)
        image_urls = []

        for image in images:
            image_urls.append(image.image.url[:-16])

        info_form = InformationFromDefectManagerForm(instance=defect)
        is_manager = is_defect_manager(request.user.id)

        return render(request, 'showDefect.html', {'defect': defect, 'image_urls': image_urls, 'info_form': info_form,
                                                   'is_defect_manager': is_manager,
                                                   "can_delete": can_delete_defect(request, defect, is_manager)})
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

    form = DefectForm(instance=defect)
    formset = DefectImageFormSet()
    images = []

    for image in DefectImage.objects.filter(defect=defect):
        images.append((image.id, image.image.url[:-16]))
    context = {'form': form, 'formset': formset, "response": request.method, "edit": True, 'images': images,
               'extra_images_number': ExtraImagesNumber, 'defect': defect}
    return render(request, 'editDefect.html', context)


@employee_required
def delete_defect(request, defect_id):
    try:
        defect = Defect.objects.get(pk=defect_id)
        if can_delete_defect(request.user.id, defect):
            images_to_delete = []
            for image in defect.image_set.all():
                images_to_delete.append(image.image.name)
            delete_images(images_to_delete)
            defect.delete()
            messages.success(request, "Pomyślnie usunięto usterkę")
            return redirect("defects:main")
        else:
            messages.error(request, "Brak odpowiednich uprawnień aby usunąć usterkę.")
            return redirect('defects:show_defect', defect_id=defect.id)
    except Defect.DoesNotExist:
        messages.error(request, "Nie istnieje usterka o podanym id.")
        return redirect('defects:main')


def can_delete_defect(request, defect, is_defect_manager_val=None):
    if is_defect_manager_val is None:
        is_defect_manager_val = is_defect_manager(request.user.id)
    return is_defect_manager_val or (defect.state == StateChoices.CREATED and defect.reporter == request.user)


@employee_required
def add_defect(request):
    """Show form for create new defect."""
    if request.method == 'POST':
        return add_defect_post_request(request)
    else:
        form = DefectForm()
        formset = DefectImageFormSet()
    context = {'form': form, 'formset': formset, "response": request.method, 'extra_images_number': ExtraImagesNumber}
    return render(request, 'editDefect.html', context)


def return_error_and_reload(request, form, edit, errors):
    messages.error(request, errors)
    formset = DefectImageFormSet()
    context = {'form': form, 'formset': formset, "response": request.method,
               'extra_images_number': ExtraImagesNumber, "edit": edit}
    return render(request, 'editDefect.html', context)


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
    selected_images = request.POST.getlist('files-to-delete[]')
    for image in selected_images:
        do_delete_image(request, image)

    if request.user.id != defect.get().reporter.id:
        defect_modified.send_robust(
            sender=Defect,
            instance=defect.get(),
            user=defect.get().reporter,
            executor=request.user
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
    try:
        formset.save()
    except Exception as exception:
        messages.error(request, "Wystąpił problem podczas zapisu zdjęć. Niektóre z nich mogły zostać niedodane.")
        logging.getLogger().error("Error during uploading files to GoogleDrive: {}".format(str(exception)))
        return redirect('defects:edit_defect', defect_id=defect.id)

    messages.success(request, "Dodano pomyślnie usterkę")
    return redirect('defects:main')


@employee_required
def print_defects(request):
    defects_list = parse_names(request.GET, "defects_ids")
    if defects_list is None or defects_list == []:
        return render(request, 'defectsPrint.html', {'defects': Defect.objects.all()})
    else:
        defects = {defect.id: defect for defect in Defect.objects.filter(pk__in=defects_list)}
        defects = [defects[i] for i in defects_list if i in defects.keys()]
        return render(request, 'defectsPrint.html', {'defects': defects})


def delete_image(request, image_id):
    if request.method == "POST":
        defect_id = do_delete_image(image_id)
        messages.success(request, "Pomyślnie usunięto zdjęcie")
        return redirect('defects:edit_defect', defect_id=defect_id)
    raise Http404


def do_delete_image(request, image_id):
    image = get_object_or_404(DefectImage, id=image_id)
    defect_id = image.defect.id
    image_path = settings.GOOGLE_DRIVE_STORAGE_DEFECT_IMAGES_DIR + image.image.name

    image.delete()

    if storage.exists(image_path):
        storage.delete(image_path)

    if request.user.id != image.defect.reporter.id:
        defect_modified.send_robust(
            sender=Defect,
            instance=image.defect,
            user=image.defect.reporter,
            executor=request.user
        )
    return defect_id


def post_information_from_defect_manager(request, defect_id):
    if request.method == "POST":
        if not is_defect_manager(request.user.id):
            messages.error(request, "Informacja o zmianach"
                                    " może zostać wypełniona tylko przez osoby do tego wyznaczone.")
            return redirect('defects:show_defect', defect_id=defect_id)
        info_form = InformationFromDefectManagerForm(request.POST)
        if not info_form.is_valid():
            messages.error(request, info_form.errors)
            return redirect('defects:show_defect', defect_id=defect_id)

        info_form_data = info_form.cleaned_data
        defect = Defect.objects.filter(pk=defect_id)
        defect.update(information_from_defect_manager=info_form_data['information_from_defect_manager'],
                      state=info_form_data["state"])

        if request.user.id != defect.get().reporter.id:
            defect_modified.send_robust(
                sender=Defect,
                instance=defect.get(),
                user=defect.get().reporter,
                executor=request.user
            )

        messages.success(request, "Pomyślnie zmodyfikowano informację o zmianach")
        return redirect('defects:show_defect', defect_id=defect_id)
    raise Http404


def is_defect_manager(user_id):
    return DefectManager.objects.filter(user_id=user_id).exists()
