import json
from functools import cmp_to_key

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.safestring import SafeText, mark_safe
from django.views.decorators.http import require_POST

from apps.grade.poll.models.last_visit import LastVisit
from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES
from apps.enrollment.courses.models import CourseInstance
from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.utils import from_plaintext
from apps.grade.ticket_create.models import PublicKey
from apps.grade.poll.models import Poll, Section, OpenQuestion, SingleChoiceQuestion, \
    MultipleChoiceQuestion, SavedTicket, SingleChoiceQuestionAnswer, \
    MultipleChoiceQuestionAnswer, OpenQuestionAnswer, Option, Template, Origin
from apps.grade.poll.forms import TicketsForm, PollForm
from apps.grade.poll.utils import check_signature, prepare_data, group_polls_and_tickets_by_course, \
    create_slug, get_next, get_prev, get_ticket_and_signed_ticket_from_session, \
    group_polls_by_course, group_polls_by_teacher, getGroups, declination_poll, \
    declination_section, declination_template, csv_prepare, generate_csv_title, get_objects, \
    delete_objects, make_paginator, groups_list, course_list, make_template_variables, \
    prepare_template, prepare_sections_for_template, prepare_data_for_create_poll, make_polls_for_groups, \
    make_message_from_polls, save_template_in_session, make_polls_for_all, get_templates, \
    make_template_from_db, get_groups_for_user, make_pages, edit_poll, prepare_data_for_create_template

from apps.users.models import Employee, Program
from apps.grade.poll.form_utils import get_section_form_data, validate_section_form, section_save
from apps.grade.poll.exceptions import NoTitleException, NoSectionException, NoPollException
from apps.users.decorators import employee_required


def main(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    return TemplateResponse(request, 'grade/main.html', locals())


@employee_required
def template_form(request, group_id=0):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data = prepare_data_for_create_poll(request, group_id)
    data['grade'] = grade
    return TemplateResponse(request, 'grade/poll/ajax_template_create.html', data)


@employee_required
def templates(request):
    """
        List of templates
        @author mjablonski
    """

    data = prepare_data_for_create_template(request)
    page, paginator = make_paginator(request, Template)
    data['semesters'] = Semester.objects.all()
    data['templates'] = page
    data['grade'] = True
    data['template_word'] = declination_template(paginator.count)
    data['pages'] = make_pages(paginator.num_pages + 1, page.number)
    data['pages_range'] = paginator.page_range
    data['tab'] = "template_list"
    return render(request, 'grade/poll/managment/templates.html', data)


@employee_required
def template_actions(request):
    """
        Action for templates
        @author mjablonski
    """
    data = {'grade': Semester.objects.filter(is_grade_active=True).count() > 0}

    if request.method == 'POST':
        action = request.POST.get('action')

        # delete
        if action == 'delete_selected':
            data['templates'] = get_objects(request, Template)
            return render(request, 'grade/poll/managment/templates_confirm.html', data)

        # use
        elif action == 'use_selected':
            semester_id = request.POST['semester']
            data['semester'] = Semester.objects.get(id=semester_id)
            data['templates'] = get_objects(request, Template)
            return render(request, 'grade/poll/managment/templates_confirm_use.html', data)

    # Nothing happend, back to list.
    return HttpResponseRedirect(reverse('grade-poll-templates'))


@employee_required
def delete_templates(request):
    if request.method == 'POST':
        counter = delete_objects(request, Template, 'templates[]')
        message = 'Usunięto ' + str(counter) + ' ' + declination_template(counter)
        messages.info(request, SafeText(message))

    return HttpResponseRedirect(reverse('grade-poll-templates'))


@employee_required
def use_templates(request):
    """
        Aply templates - make polls!
        @author mjablonski
    """
    if request.method == 'POST':
        try:
            templates = get_templates(request)
            create_poll_from_template(request, templates)
        except NoTitleException:
            messages.error(request, "Nie można utworzyć ankiety; brak tytułu")
            return HttpResponseRedirect(reverse('grade-poll-templates'))
        except NoSectionException:
            messages.error(request, "Nie można utworzyć ankiety; ankieta jest pusta")
            return HttpResponseRedirect(reverse('grade-poll-templates'))
        except NoPollException:
            messages.info(request, "Nie utworzono żadnej ankiety")
            return HttpResponseRedirect(reverse('grade-poll-templates'))
    return HttpResponseRedirect(reverse('grade-poll-templates'))


def create_poll_from_template(request, templates):
    polls_list = []
    for tmpl in templates:
        template = make_template_from_db(request, tmpl)
        groups = getGroups(request, template)
        if groups:
            polls = []
            origin = Origin()
            origin.save()
            for group in groups:
                if template['groups_without'] == 'on' and Poll.get_all_polls_for_group(
                        group, template.semeter).count() > 0:
                    continue

            polls = make_polls_for_groups(request, groups, template)
        else:
            polls = make_polls_for_all(request, template)
        polls_list.extend(polls)
    message = make_message_from_polls(polls_list)
    messages.success(request, message)

    return len(message)


@employee_required
def show_template(request, template_id):
    template = Template.objects.get(pk=template_id)
    form = PollForm()
    form.setFields(template)
    data = {
        'form': form,
        'template': template,
        'grade': Semester.objects.filter(
            is_grade_active=True).count() > 0}
    if request.is_ajax():
        return render(request, 'grade/poll/managment/ajax_show_template.html', data)
    else:
        return render(request, 'grade/poll/managment/show_poll.html', data)


# save poll as template
# @author mjablonski

@employee_required
def create_template(request):
    if request.method != "POST":
        raise Http404

    template = prepare_template(request)
    prepare_sections_for_template(request, template)

    return HttpResponseRedirect(reverse('grade-poll-templates'))


def rules(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    return render(request, 'grade/rules.html', {'grade': grade})


@employee_required
def enable_grade(request):
    if request.method == 'POST':
        sid = request.POST.get('semester_id')
        try:
            semester = Semester.objects.get(id=sid)
        except ObjectDoesNotExist:
            semester = None
            messages.error(request, "Podany semester nie istnieje")

        if semester:
            if semester.is_grade_active:
                messages.error(request, "Nie można otworzyć oceny; ocena jest już otwarta")
            elif not Poll.get_polls_for_semester(semester=semester).count():
                messages.error(request, "Nie można otworzyć oceny; brak ankiet")
            elif Poll.get_semester_polls_without_keys(semester=semester).count():
                messages.error(request, "Nie można otworzyć oceny; brak kluczy dla ankiet")
            else:
                semester.is_grade_active = True
                semester.save()
                messages.success(request, "Ocena zajęć otwarta")

    data = dict(
        semesters=Semester.objects.all()
    )

    return render(request, 'grade/enable.html', data)


@employee_required
def disable_grade(request):
    semester_id = request.POST.get('semester_id')
    semester = Semester.objects.get(id=semester_id)

    if semester.is_grade_active:
        semester.is_grade_active = False
        semester.save()

        #        PublicKey.objects.all().delete()
        #        PrivateKey.objects.all().delete()

        for st in SavedTicket.objects.filter(finished=False):
            # TODO: oznaczyć je jako archiwalne!
            st.finished = True
            st.save()

        messages.success(request, "Zamknięto ocenę zajęć")
    else:
        messages.error(request, "Nie można zamknąć oceny; system nie był uruchomiony")

    return HttpResponseRedirect(reverse('grade-main'))


"""Poll creation"""


@employee_required
def autocomplete(request):
    results = []
    if request.method == "GET":
        if 'term' in request.GET:
            value = request.GET['term']
            # Ignore queries shorter than length 3
            # if len(value) > 2:
            model_results = Option.objects.filter(content__istartswith=value). \
                distinct().values_list('content', flat=True)
            results = [x for x in model_results]
    if results:
        json_ = json.dumps(results)
    else:
        json_ = ""
    return HttpResponse(json_, content_type='application/javascript')


@employee_required
def ajax_get_groups(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            type = int(request.POST.get('type', '0'))
            course = int(request.POST.get('course', '0'))
            groups = groups_list(get_groups_for_user(request, type, course))
            message = json.dumps(groups)
    return HttpResponse(message)


@employee_required
def ajax_get_courses(request):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            semester = int(request.POST.get('semester', '0'))
            courses = course_list(CourseInstance.objects.filter(semester=semester).order_by('name'))
            message = json.dumps(courses)
    return HttpResponse(message)


@employee_required
def edit_section(request, section_id):
    form = PollForm()
    form.setFields(None, None, section_id)
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    return render(request, 'grade/poll/section_edit.html', {"form": form, 'grade': grade})


@employee_required
def poll_form(request, group_id=0):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data = prepare_data_for_create_poll(request, group_id)
    data['grade'] = grade
    return render(request, 'grade/poll/ajax_poll_create.html', data)


@employee_required
def poll_edit_form(request, poll_id):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    poll = Poll.objects.get(pk=poll_id)
    data = prepare_data_for_create_poll(request)

    poll.forms = []

    for section in poll.all_sections():
        form = PollForm()
        form.setFields(None, None, section.pk)
        form.sid = section.pk
        poll.forms.append(form)

    data['grade'] = grade
    data['poll'] = poll
    return render(request, 'grade/poll/ajax_poll_edit.html', data)


@employee_required
def poll_edit(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        messages.error(
            request,
            "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona")
        return HttpResponseRedirect(reverse('grade-main'))

    if request.method == "POST":
        for_all = (request.POST.get('for_all') == 'on')
        poll_id = int(request.POST['poll_id'])
        poll = Poll.objects.get(pk=poll_id)
        if for_all and poll.origin:
            origin = poll.origin
            polls = Poll.objects.filter(origin=origin)
            for edited_poll in polls:
                edit_poll(edited_poll, request, origin)
            messages.success(request, "Ankiety zostały zmienione")
        else:
            origin = Origin()
            origin.save()
            edit_poll(poll, request, origin)
            messages.success(request, "Ankieta została zmieniona")

    return HttpResponseRedirect(reverse('grade-main'))


@employee_required
def poll_create_for_group():
    pass


@employee_required
def poll_create(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        messages.error(
            request,
            "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona")
        return HttpResponseRedirect(reverse('grade-main'))

    if request.method == "POST":
        try:
            template = make_template_variables(request)
            groups = getGroups(request, template)
            if groups:
                polls = make_polls_for_groups(request, groups, template)
            else:
                polls = make_polls_for_all(request, template)
            message = make_message_from_polls(polls)

            template['polls_len'] = len(polls)
            messages.success(request, message)
            save_template_in_session(request, template)
            return HttpResponseRedirect(reverse('grade-poll-poll-create'))

        except NoTitleException:
            messages.error(request, "Nie można utworzyć ankiety; brak tytułu")
            return HttpResponseRedirect(reverse('grade-main'))
        except NoSectionException:
            messages.error(request, "Nie można utworzyć ankiety; ankieta jest pusta")
            return HttpResponseRedirect(reverse('grade-main'))
        except NoPollException:
            messages.info(request, "Nie utworzono żadnej ankiety")
            return HttpResponseRedirect(reverse('grade-main'))

    return HttpResponseRedirect(reverse('grade-main'))


#
# Poll managment
#

@employee_required
def sections_list(request):
    """
        Preparation of sections list; if user is member of the staff he will also
        be able to edit and delete sections; employees without special privileges
        aren't allowed to any such action.
    """
    data = {}
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        messages.error(
            request,
            "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona")
        return HttpResponseRedirect(reverse('grade-main'))
    page, paginator = make_paginator(request, Section)
    data['sections'] = page
    data['sections_word'] = declination_section(paginator.count, True)
    data['grade'] = grade
    data['pages'] = make_pages(paginator.num_pages + 1, page.number)
    data['pages_range'] = paginator.page_range
    data['tab'] = "section_list"
    return render(request, 'grade/poll/managment/sections_list.html', data)


@employee_required
def show_section(request, section_id):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    if grade:
        messages.error(
            request,
            "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona")
        return HttpResponseRedirect(reverse('grade-main'))
    form = PollForm()
    form.setFields(None, None, section_id)
    data = {}
    data['form'] = form
    data['grade'] = grade
    data['section'] = Section.objects.get(pk=section_id)

    if request.is_ajax():
        return render(request, 'grade/poll/managment/ajax_show_section.html', data)
    else:
        return render(request, 'grade/poll/managment/show_section.html', data)


@employee_required
def get_section(request, section_id):
    form = PollForm()
    form.setFields(None, None, section_id)
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    return render(request, 'grade/poll/poll_section.html',
                  {"form": form, "section_id": section_id, 'grade': grade})


@employee_required
def section_actions(request):
    data = {}
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data['grade'] = grade
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_selected':
            data['sections'] = get_objects(request, Section)
            return render(request, 'grade/poll/managment/section_confirm_delete.html', data)

    return HttpResponseRedirect(reverse('grade-poll-sections-list'))


@employee_required
def delete_sections(request):
    if request.method == 'POST':
        counter = delete_objects(request, Section, 'sections[]')
        message = 'Usunięto ' + str(counter) + ' ' + declination_section(counter)
        messages.info(request, SafeText(message))

    return HttpResponseRedirect(reverse('grade-poll-sections-list'))


@employee_required
def show_poll(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    form = PollForm()
    form.setFields(poll, None, None)
    data = {}
    data['form'] = form
    data['poll_id'] = poll_id
    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0
    if request.is_ajax():
        return render(request, 'grade/poll/managment/ajax_show_poll.html', data)
    else:
        return render(request, 'grade/poll/managment/show_poll.html', data)


@employee_required
def poll_actions(request):
    data = {}
    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_selected':
            data['polls'] = get_objects(request, Poll)
            return render(request, 'grade/poll/managment/poll_confirm_delete.html', data)
    return HttpResponseRedirect(reverse('grade-main'))


@employee_required
def delete_polls(request):
    if request.method == 'POST':
        counter = delete_objects(request, Poll, 'polls[]')
        message = 'Usunięto ' + str(counter) + ' ' + declination_poll(counter)
        messages.info(request, SafeText(message))

    return HttpResponseRedirect(reverse('grade-main'))


@employee_required
def groups_without_poll(request):
    data = {}
    data['groups'] = Poll.get_groups_without_poll()
    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0
    data['tab'] = "group_without"
    return render(request, 'grade/poll/managment/groups_without_polls.html', data)


@employee_required
def poll_manage(request):
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data = {}
    data['semesters'] = Semester.objects.all()
    data['grade'] = grade
    return render(request, 'grade/poll/manage.html', data)


@employee_required
def get_section_form(request):
    data = {}
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data['grade'] = grade

    return render(request, 'grade/poll/ajax_section_create.html', data)


@employee_required
def questionset_create(request):
    data = {}
    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data['grade'] = grade

    if grade:
        messages.error(
            request,
            "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona")
        return HttpResponseRedirect(reverse('grade-main'))

    if request.method == "POST":
        form_data = get_section_form_data(request.POST)
        errors = validate_section_form(form_data)

        if errors:
            error_msg = "Nie można utworzyć sekcji:\n<ul>"
            if 'title' in errors:
                error_msg += "<li>" + errors['title'] + "</li>"
            if 'content' in errors:
                error_msg += "<li>" + errors['content'] + "</li>"
            if 'questions' in errors:
                question_errors = sorted(errors['questions'].keys())
                for position in question_errors:
                    error_msg += "<li>Pytanie " + str(position) + ":\n<ul>"
                    for error in errors['questions'][position]:
                        error_msg += "<li>" + error + "</li>"
                    error_msg += "</ul></li>"
            error_msg += "</ul>"

            messages.error(request, SafeText(error_msg))
        else:
            if section_save(form_data):
                messages.success(request, "Sekcja dodana")
            else:
                messages.error(request, "Zapis sekcji nie powiódł się")

        return HttpResponseRedirect('/grade/poll/managment/sections_list')

    return HttpResponseRedirect('/grade/poll/managment/sections_list')


"""Poll answering"""


@login_required
def grade_logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('grade-poll-tickets-enter'))


def tickets_enter(request):
    if request.user.is_authenticated:
        return render(request, 'grade/poll/user_is_authenticated.html', {'grade': True})

    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    data = {}

    if request.method == "POST":
        form = TicketsForm(request.POST, request.FILES)

        if form.is_valid():
            if request.FILES:
                keysfile = request.FILES['ticketsfile']
                if keysfile.size > 1048576:
                    from django.template.defaultfilters import filesizeformat
                    messages.error(request,
                                   'Proszę przesłać plik o maksymalnym rozmiarze: \
                        %s. Obecny rozmiar to: %s' %
                                   (filesizeformat(1048576), filesizeformat(keysfile.size)))
                    data['form'] = form
                    data['grade'] = grade
                    return render(request, 'grade/poll/tickets_enter.html', data)
                else:
                    tickets_plaintext = keysfile.read()
            else:
                tickets_plaintext = form.cleaned_data['ticketsfield']
            try:
                ids_and_tickets = from_plaintext(tickets_plaintext)
            except BaseException:
                ids_and_tickets = []

            if not ids_and_tickets:
                messages.error(request, "Podano niepoprawne bilety.")
                data['form'] = form
                data['grade'] = grade
                return render(request, 'grade/poll/tickets_enter.html', data)

            errors = []
            polls = []
            finished = []
            for (id, (ticket, signed_ticket)) in ids_and_tickets:
                try:
                    poll = Poll.objects.get(pk=id)
                    public_key = PublicKey.objects.get(poll=poll)
                    if check_signature(ticket, signed_ticket, public_key):
                        try:
                            st = SavedTicket.objects.get(poll=poll,
                                                         ticket=ticket)
                            if st.finished:
                                finished.append((poll, ticket, signed_ticket))
                            else:
                                polls.append((poll, ticket, signed_ticket))
                        except BaseException:
                            st = SavedTicket(poll=poll, ticket=ticket)
                            st.save()
                            polls.append((poll, ticket, signed_ticket))
                    else:
                        errors.append((id, "Nie udało się zweryfikować podpisu pod biletem."))
                except BaseException:
                    errors.append((id, "Podana ankieta nie istnieje"))

            if errors:
                msg = "Wystąpił problem z biletami na następujące ankiety: <ul>"
                for pid, error in errors:
                    try:
                        poll = str(Poll.objects.get(pk=pid))
                    except BaseException:
                        poll = str(pid)
                    msg += '<li>' + poll + " - " + error + '</li>'
                msg += '</ul>'
                msg = mark_safe(str(msg))
                messages.error(request, msg)
            request.session["polls"] = [
                (
                    (poll_name, create_slug(poll_name)),
                    poll_list,
                ) for poll_name, poll_list in group_polls_and_tickets_by_course(polls)
            ]
            request.session["finished"] = [
                (
                    (poll_name, create_slug(poll_name)),
                    poll_list,
                ) for poll_name, poll_list in group_polls_and_tickets_by_course(finished)
            ]

            return HttpResponseRedirect('/grade/poll/polls/all')
    else:
        form = TicketsForm()

    data['form'] = form
    data['grade'] = grade
    return render(request, 'grade/poll/tickets_enter.html', data)


def polls_for_user(request, slug):
    if 'polls' not in request.session:
        return HttpResponseRedirect(reverse('grade-poll-tickets-enter'))

    data = prepare_data(request, slug)
    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0
    if data['polls']:
        (_, s), _, list_ = data['polls'][0]
        id_, _, _, _ = list_[0]
        return HttpResponseRedirect(reverse('grade-poll-poll-answer', args=[s, id_]))
    elif data['finished']:
        (_, s), _, list_ = data['finished'][0]
        id_, _, _, _ = list_[0]
        return HttpResponseRedirect(reverse('grade-poll-poll-answer', args=[s, id_]))

    return render(request, 'grade/poll/polls_for_user.html', data)


def slug_cmp(t1, t2):
    x = t1[0]
    y = t2[0]
    slug1 = x[1]
    slug2 = y[1]
    if slug1 == "common":
        return -1
    if slug2 == "common":
        return 1
    return (x > y) - (x < y)


def poll_answer(request, slug, pid):
    if request.user.is_authenticated:
        return render(request, 'grade/poll/user_is_authenticated.html', {})

    poll = Poll.objects.get(pk=pid)
    public_key = PublicKey.objects.get(poll=poll)

    (ticket, signed_ticket) = get_ticket_and_signed_ticket_from_session(request.session, slug, pid)

    data = prepare_data(request, slug)
    data['link_name'] = poll.to_url_title()
    data['slug'] = slug
    data['title'] = poll.title
    data['desc'] = poll.description
    data['pid'] = pid

    try:
        poll_cands = []
        for poll_to_show in data['polls']:

            polls = []
            for poll_details in poll_to_show[2]:
                polls.append((poll_details, poll_to_show[0][1]))

            poll_cands.extend(polls)

    except IndexError:
        poll_cands = []

    try:

        finished_cands = []
        for poll_to_show in data['finished']:

            polls = []
            for poll_details in poll_to_show[2]:
                polls.append((poll_details, poll_to_show[0][1]))

            finished_cands.extend(polls)
    except BaseException:
        finished_cands = []

    data['next'] = get_next(poll_cands, finished_cands, int(pid))
    data['prev'] = get_prev(poll_cands, finished_cands, int(pid))

    if ticket and signed_ticket and check_signature(ticket, signed_ticket, public_key):
        st = SavedTicket.objects.get(ticket=str(ticket), poll=poll)

        if request.method == "POST" and not st.finished:
            form = PollForm()
            form.setFields(poll, st, None, request.POST)

            errors = {}
            for key in request.POST:
                if key in form.fields:
                    if form.fields[key].type == 'multi':
                        field_data = request.POST.getlist(key)
                    else:
                        field_data = request.POST[key]
                    try:
                        form.fields[key].clean(field_data)
                        """
                        except ValidationError as ve:
                        errors[ key ] = ve.messages
                        """
                    except ValidationError:
                        errors[key] = ""

            if errors:
                data['form_errors'] = errors
                messages.error(
                    request,
                    "Nie udało się zapisać ankiety: " +
                    poll.title +
                    "; błąd formularza")
            else:
                data['form_errors'] = {}
                keys = list(form.fields.keys())
                keys.remove('finish')
                keys.sort()
                section_data = []

                if keys:
                    act = [keys[0]]
                    curr_id = keys[0].split('_')[1].split('-')[1]
                    for key in keys[1:]:
                        sect_id = key.split('_')[1].split('-')[1]
                        if sect_id == curr_id:
                            act.append(key)
                        else:
                            section_data.append((curr_id, act))
                            curr_id = sect_id
                            act = [key]
                    if act:
                        section_data.append((curr_id, act))

                for section_id, section_answers in section_data:
                    section = Section.objects.get(pk=section_id)
                    delete = False
                    if section_answers[0].endswith('leading'):
                        question_id = section_answers[0].split('_')[2].split('-')[1]
                        question = SingleChoiceQuestion.objects.get(
                            pk=question_id)
                        try:
                            ans = SingleChoiceQuestionAnswer.objects.get(
                                section=section,
                                question=question,
                                saved_ticket=st)
                        except ObjectDoesNotExist:
                            ans = SingleChoiceQuestionAnswer(
                                section=section,
                                question=question,
                                saved_ticket=st)
                            ans.save()
                        ansx = request.POST.get(section_answers[0], None)
                        if ansx:
                            option = Option.objects.get(pk=ansx)
                            ans.option = option
                            ans.save()
                            if option in question.singlechoicequestionordering_set.filter(
                                    sections=section)[0].hide_on.all():
                                delete = True
                        else:
                            ans.delete()
                            delete = True
                        section_answers = section_answers[1:]

                    for answer in section_answers:
                        question_id = answer.split('_')[2].split('-')[1]
                        question_type = answer.split('_')[2].split('-')[2]
                        if not answer.endswith('other'):
                            if question_type == 'single':
                                question = SingleChoiceQuestion.objects.get(
                                    pk=question_id)
                                try:
                                    ans = SingleChoiceQuestionAnswer.objects.get(
                                        question=question,
                                        saved_ticket=st)
                                except ObjectDoesNotExist:
                                    ans = SingleChoiceQuestionAnswer(
                                        section=section,
                                        question=question,
                                        saved_ticket=st)
                                    ans.save()

                                value = request.POST.get(answer, None)
                                if delete:
                                    ans.delete()
                                elif value:
                                    ans.option = Option.objects.get(pk=value)
                                    ans.save()
                                else:
                                    ans.delete()
                            if question_type == 'open':
                                question = OpenQuestion.objects.get(
                                    pk=question_id)
                                try:
                                    ans = OpenQuestionAnswer.objects.get(
                                        question=question,
                                        saved_ticket=st)
                                except ObjectDoesNotExist:
                                    ans = OpenQuestionAnswer(
                                        section=section,
                                        question=question,
                                        saved_ticket=st)
                                    ans.save()

                                value = request.POST.get(answer, None)
                                if delete:
                                    ans.delete()
                                elif value:
                                    ans.content = value
                                    ans.save()
                                else:
                                    ans.delete()
                            if question_type == 'multi':
                                question = MultipleChoiceQuestion.objects.get(
                                    pk=question_id)
                                try:
                                    ans = MultipleChoiceQuestionAnswer.objects.get(
                                        question=question,
                                        saved_ticket=st)
                                except ObjectDoesNotExist:
                                    ans = MultipleChoiceQuestionAnswer(
                                        section=section,
                                        question=question,
                                        saved_ticket=st)
                                    ans.save()

                                value = request.POST.getlist(answer)
                                if delete:
                                    ans.delete()
                                elif value:
                                    if '-1' in value:
                                        ans.other = request.POST.get(answer + '-other', None)
                                        value.remove('-1')
                                    else:
                                        ans.other = None
                                    ans.options = []
                                    options = Option.objects.filter(pk__in=value)
                                    for option in options:
                                        ans.options.add(option)
                                    ans.save()
                                else:
                                    ans.delete()
                if 'finish' in request.POST:
                    messages.success(request, "Ankieta: " + poll.title + " zakończona")
                    finit = request.session.get('finished', default=[])
                    polls = request.session.get('polls', default=[])

                    slug_polls = [x_s_ls for x_s_ls in polls if slug == x_s_ls[0][1]]
                    slug_finit = [x_s_ls1 for x_s_ls1 in finit if slug == x_s_ls1[0][1]]

                    name = None

                    for ((n, s), ls) in slug_polls:
                        pd = [x for x in ls if x == (int(pid), ticket, signed_ticket)]
                        if pd:
                            polls.remove(((n, s), ls))
                            for poll_data in pd:
                                ls.remove(poll_data)
                            if ls:
                                polls.append(((n, s), ls))
                            name = n
                            break

                    if slug_finit:
                        for ((n, s), ls) in slug_finit:
                            if n == name:
                                finit.remove(((n, s), ls))
                                ls.append((int(pid), ticket, signed_ticket))
                                finit.append(((n, s), ls))
                                break
                    else:
                        finit.append(((name, slug), [(int(pid), ticket, signed_ticket)]))

                    polls.sort(key=cmp_to_key(slug_cmp))
                    finit.sort(key=cmp_to_key(slug_cmp))

                    request.session['finished'] = finit
                    request.session['polls'] = polls

                    st.finished = True
                    st.save()
                else:
                    messages.success(request, "Ankieta: " + poll.title + " zapisana")
        else:
            form = PollForm()
            form.setFields(poll, st)

        # This is needed so that template code in poll_answer doesn't
        # crash the server - {% if form.finish %} should work
        # but ends up crashing gunicorn
        if not hasattr(form, "finish"):
            form.finish = None

        data['form'] = form
        data['pid'] = int(pid)

        if request.method == "POST" and (
                not ('form_errors' in data and data['form_errors']) or st.finished):
            if request.POST.get('Next', default=None):
                return HttpResponseRedirect('/grade/poll/poll_answer/' +
                                            str(data['next'][3]) + '/' + str(data['next'][0]))
            if request.POST.get('Prev', default=None):
                return HttpResponseRedirect('/grade/poll/poll_answer/' +
                                            str(data['prev'][3]) + '/' + str(data['prev'][0]))
            if request.POST.get('Save', default=None):
                return HttpResponseRedirect('/grade/poll/poll_answer/' + slug + '/' + str(pid))
    else:
        data = {'errors': ["Nie masz uprawnień do wypełnienia ankiety " + poll.to_url_title()],
                'slug': slug,
                'link_name': poll.to_url_title()}

    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0

    return render(request, 'grade/poll/poll_answer.html', data)


def poll_end_grading(request):
    request.session.clear()

    return HttpResponseRedirect(reverse('grade-main'))


"""Poll results"""


@login_required
def poll_results(request, mode='S', poll_id=None, semester=None):
    data = {}
    try:
        if not semester:
            semester = Semester.get_current_semester()
        else:
            semester = Semester.objects.get(id=semester)
    except ObjectDoesNotExist:
        raise Http404

    data['grade'] = semester.is_grade_active
    data['semester'] = semester
    data['semesters'] = Semester.objects.all()

    if mode == 'S':
        data['mode'] = 'course'
    elif mode == 'T':
        data['mode'] = 'teacher'

    if semester.is_grade_active:
        messages.info(request, "Ocena zajęć jest otwarta; wyniki nie są kompletne.")

    if not poll_id:
        polls = [
            x for x in Poll.get_polls_for_semester(
                semester=semester) if x.is_user_entitled_to_view_result(
                request.user)]
        request.session['polls_by_course'] = group_polls_by_course(polls)
        request.session['polls_by_teacher'] = group_polls_by_teacher(polls)

    try:
        data['polls_by_course'] = request.session['polls_by_course']
        data['polls_by_teacher'] = request.session['polls_by_teacher']
    except BaseException:
        polls = [x for x in Poll.get_polls_for_semester(
        ) if x.is_user_entitled_to_view_result(request.user)]
        request.session['polls_by_course'] = group_polls_by_course(polls)
        request.session['polls_by_teacher'] = group_polls_by_teacher(polls)
        data['polls_by_course'] = request.session['polls_by_course']
        data['polls_by_teacher'] = request.session['polls_by_teacher']

    if poll_id:
        data['pid'] = int(poll_id)
        data['link_mode'] = mode
        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            messages.error(request, "Podana ankieta nie istnieje.")
            return render(request, 'grade/poll/poll_total_results.html', data)

        last_visit, created = LastVisit.objects.get_or_create(user=request.user, poll=poll)
        data['last_visit'] = last_visit.time
        last_visit.save()

        if poll.is_user_entitled_to_view_result(request.user):
            poll_answers = poll.all_answers()
            sts_fin = SavedTicket.objects.filter(poll=poll, finished=True).count()
            sts_not_fin = SavedTicket.objects.filter(poll=poll, finished=False).count()
            sts_all = sts_fin + sts_not_fin

            answers = []
            for section, section_answers in poll_answers:
                s_ans = []
                for question, question_answers in section_answers:
                    if isinstance(question, SingleChoiceQuestion):
                        mode = 'single'
                        q_data = [x.option for x in question_answers]
                        options = question.options.all()
                        ans_data = []
                        for option in options:
                            if sts_all:
                                perc = int(100 * (float(q_data.count(option)) / float(sts_all)))
                            else:
                                perc = 0
                            ans_data.append((option.content, q_data.count(option), perc))
                        if sts_all:
                            perc = int(100 * (float(sts_all - len(question_answers)) / float(sts_all)))
                        else:
                            perc = 0
                        ans_data.append(("Brak odpowiedzi", sts_all - len(question_answers), perc))
                        s_ans.append((mode, question.content, ans_data, (100 / len(ans_data)) - 1))

                    elif isinstance(question, MultipleChoiceQuestion):
                        mode = 'multi'
                        q_data = [(list(x.options.all()), x.other) for x in question_answers]
                        if q_data:
                            q_data, other_data = list(zip(*q_data))
                            q_data = sum(q_data, [])
                            other_data = [x for x in other_data if x]
                        else:
                            other_data = []
                        options = question.options.all()
                        ans_data = []
                        for option in options:
                            if sts_all:
                                perc = int(100 * (float(q_data.count(option)) / float(sts_all)))
                            else:
                                perc = 0
                            ans_data.append((option.content, q_data.count(option), perc))
                        if question.has_other:
                            if sts_all:
                                perc = int(100 * (float(len(other_data)) / float(sts_all)))
                            else:
                                perc = 0
                            ans_data.append(("Inne", len(other_data), perc, other_data))
                        if sts_all:
                            perc = int(100 * (float(sts_all - len(question_answers)) / float(sts_all)))
                        else:
                            perc = 0
                        ans_data.append(("Brak odpowiedzi", sts_all - len(question_answers), perc))
                        s_ans.append((mode, question.content, ans_data, (100 / len(ans_data)) - 1))

                    elif isinstance(question, OpenQuestion):
                        mode = 'open'
                        s_ans.append(
                            (mode, question.content, question_answers, len(question_answers)))

                answers.append((section.title, s_ans))

            if semester.is_grade_active:
                data['completness'] = SafeText(
                    "Liczba studentów, którzy zakończyli wypełniać ankietę: %d<br/>Liczba studentów którzy nie zakończyli wypełniać ankiety: %d" %
                    (sts_fin, sts_not_fin))
            else:
                data['completness'] = SafeText(
                    "Liczba studentów, którzy wypełnili ankietę: %d" %
                    (sts_fin))
            data['poll_title'] = poll.title
            try:
                data['poll_course'] = poll.group.course.name
                data['poll_group'] = poll.group.get_type_display()
                data['poll_teacher'] = poll.group.get_teacher_full_name()
            except BaseException:
                data['poll_course'] = "Ankieta ogólna"

            try:
                user = poll.group.teacher
            except BaseException:
                user = None

            if user:
                if user == request.user:
                    data['show_share_toggle'] = True
            else:
                data['show_share_toggle'] = request.user.is_superuser

            data['share_state'] = poll.share_result
            data['results'] = answers
        else:
            messages.error(request, "Nie masz uprawnień do oglądania wyników tej ankiety.")

    return render(request, 'grade/poll/poll_total_results.html', data)


@login_required
def poll_results_detailed(request, mode, poll_id, st_id=None, semester=None):
    data = {}
    data['grade'] = Semester.objects.filter(is_grade_active=True).count() > 0

    if mode == 'S':
        data['mode'] = 'course'
    elif mode == 'T':
        data['mode'] = 'teacher'

    try:
        if not semester:
            semester = Semester.get_current_semester()
        else:
            semester = Semester.objects.get(id=semester)
    except ObjectDoesNotExist:
        raise Http404

    data['semester'] = semester
    data['semesters'] = Semester.objects.all()

    if semester.is_grade_active:
        messages.info(request, "Ocena zajęć jest otwarta; wyniki nie są kompletne.")

    try:
        data['polls_by_course'] = request.session['polls_by_course']
        data['polls_by_teacher'] = request.session['polls_by_teacher']
    except BaseException:
        polls = [x for x in Poll.get_polls_for_semester(
        ) if x.is_user_entitled_to_view_result(request.user)]
        request.session['polls_by_course'] = group_polls_by_course(polls)
        request.session['polls_by_teacher'] = group_polls_by_teacher(polls)
        data['polls_by_course'] = request.session['polls_by_course']
        data['polls_by_teacher'] = request.session['polls_by_teacher']

    data['pid'] = poll_id
    data['link_mode'] = mode
    try:
        poll = Poll.objects.get(id=poll_id)
    except BaseException:
        messages.error(request, "Podana ankieta nie istnieje.")
        return render(request, 'grade/poll/poll_total_results.html', data)

    if poll.is_user_entitled_to_view_result(request.user):

        if not st_id:
            sts = SavedTicket.objects.filter(poll=poll, finished=True)
            data['page'] = 1
            data['sts'] = sts
            request.session['sts'] = data['sts']
        else:
            try:
                data['sts'] = request.session['sts']
            except BaseException:
                sts = SavedTicket.objects.filter(poll=poll, finished=True)
                data['sts'] = sts
                request.session['sts'] = data['sts']

            sts = data['sts']
            data['page'] = 1
            err = True
            for i, st in enumerate(sts):
                if str(st.id) == str(st_id):
                    data['page'] = i + 1
                    err = False
                    break
            if err:
                messages.error(request, "Nie istnieje taka odpowiedź na ankietę")

        sts = list(sts)
        if sts:
            st = sts[data['page'] - 1]

            form = PollForm()
            form.setFields(poll, st)
            data['form'] = form

            data['first'] = sts[0].id
            data['last'] = sts[-1].id
            data['connected'] = []
            for cst in SavedTicket.objects.filter(
                    ticket=st.ticket,
                    finished=True).exclude(poll=poll):
                cform = PollForm()
                cform.setFields(cst.poll, cst)
                data['connected'].append(cform)

            pages = []
            for i, t in enumerate(data['sts']):
                pages.append((i + 1, t.id))
            beg = data['page'] - 10
            if beg < 1:
                beg = 1
            end = beg + 50
            data['pages'] = pages[beg - 1:end - 1]
        else:
            messages.error(request, "Brak odpowiedzi na tą ankietę.")

    else:
        messages.error(request, "Nie masz uprawnień do oglądania wyników tej ankiety.")

    return render(request, 'grade/poll/poll_detailed_results.html', data)


@login_required
def save_csv(request, mode, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except ObjectDoesNotExist:
        raise Http404

    csv_title = generate_csv_title(poll)

    # For each section: section title and contents of all questions
    poll_answers = poll.all_answers()
    sections = []
    for section, section_answers in poll_answers:
        sections.append(['[' + str(section.title) + ']' + str(q.content)
                         for q in section.all_questions()])

    # For each ticket (that is, response to the poll): answers to all questions
    poll_answers = poll.all_answers_by_tickets()
    answers = []
    for ticket, sections_list in poll_answers:
        answer = []
        for section, section_answers in sections_list:
            # Actual answers to these questions
            for question, question_answer in section_answers:
                if not question_answer:
                    answer.append('')
                else:
                    answer.append(str(question_answer[0]))
        answers.append(answer)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format(csv_title)
    csv_content = csv_prepare(response, sections, answers)
    return response


@login_required
def share_results_toggle(request, mode, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    poll.share_result = not poll.share_result
    poll.save()
    if poll.share_result:
        messages.info(request, "Udostępniono wyniki ankiety.")
    else:
        messages.info(request, "Przestano udostepniać wyniki ankiety.")
    return HttpResponseRedirect(reverse('grade-poll-poll-results', args=[mode, poll_id]))


@login_required()
@require_POST
def change_semester(request):
    semester = request.POST.get('semester', None)
    if not semester:
        raise Http404

    return redirect('grade-poll-poll-results-semester', semester=int(semester), mode='S')
