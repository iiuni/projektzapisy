# -*- coding: utf-8 -*-
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
import operator


from apps.schedule.filters import EventFilter, ExamFilter
from apps.schedule.forms import EventForm, TermFormSet, DecisionForm, EventModerationMessageForm, EventMessageForm
from apps.schedule.utils import EventAdapter
from apps.utils.fullcalendar import FullCalendarView

__author__ = 'maciek'


def classrooms(request):
    from apps.enrollment.courses.models import Classroom

    rooms = Classroom.get_in_institute(reservation=True)
    return TemplateResponse(request, 'schedule/classrooms.html', locals())


def classroom(request, slug):
    from apps.enrollment.courses.models import Classroom

    rooms = Classroom.get_in_institute(reservation=True)
    try:
        room = Classroom.get_by_slug(slug)
    except ObjectDoesNotExist:
        raise Http404

    return TemplateResponse(request, 'schedule/classroom.html', locals())


@login_required
def reservation(request, event_id=None):
    from apps.schedule.models import Event

    form = EventForm(data=request.POST or None, user=request.user)

    if form.is_valid():
        event = form.save(commit=False)
        event.author = request.user
        formset = TermFormSet(request.POST or None, instance=event)
        if formset.is_valid():
            event.save()
            formset.save()

            return redirect(event)
    else:
        formset = TermFormSet(data=request.POST or None, instance=Event())

    return TemplateResponse(request, 'schedule/reservation.html', locals())


@login_required
def edit_event(request, event_id=None):
    from apps.schedule.models import Event

    is_edit = True

    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventForm(data=request.POST or None, instance=event, user=request.user)
    formset = TermFormSet(request.POST or None, instance=event)
    reservation = event.reservation

    if form.is_valid() and formset.is_valid():
        event = form.save(commit=False)
        if not event.id:
            event.author = request.user
        event.reservation = reservation
        event.save()
        formset.save()

        messages.success(request, u'Zmieniono zdarzenie')

        return redirect(event)

    return TemplateResponse(request, 'schedule/reservation.html', locals())


def session(request, semester=None):
    from apps.schedule.models import Term
    from apps.enrollment.courses.models import Semester

    exams = ExamFilter(request.GET, queryset=Term.get_exams())

    if semester:
        semester = Semester.get_by_id(semester)
    else:
        semester = Semester.get_current_semester()

    return TemplateResponse(request, 'schedule/session.html', locals())


@login_required
def reservations(request):
    from apps.schedule.models import Event
    events = EventFilter(request.GET, queryset=Event.get_all_without_courses())
    title = u'Zarządzaj rezerwacjami'
    return TemplateResponse(request, 'schedule/reservations.html', locals())


@login_required
def history(request):
    from apps.schedule.models import Event

    events = EventFilter(request.GET, queryset=Event.get_for_user(request.user))
    title = u'Moje rezerwacje'
    return TemplateResponse(request, 'schedule/history.html', locals())


@require_POST
def decision(request, event_id):
	from apps.schedule.models import Event
	from .models.message import EventModerationMessage

	event = Event.get_event_for_moderation_only_or_404(event_id, request.user)

	form = DecisionForm(request.POST, instance=event)
	
	event_status = event.status
	
	if form.is_valid():
		if event_status == form.cleaned_data['status']:
			messages.error(request, u'Status wydarzenia nie został zmieniony')
		else:
			event_obj = form.save()
			msg = EventModerationMessage()
			msg.author = request.user
			msg.message = u'Status wydarzenia został zmieniony na ' + unicode(event_obj.get_status_display())
			msg.event = event_obj
			msg.save()
			messages.success(request, u'Status wydarzenia został zmieniony')
	
	return redirect(reverse('events:show', args=[str(event.id)]))


def events(request):
    return TemplateResponse(request, 'schedule/events.html', locals())


@login_required
def event(request, event_id):
    from apps.schedule.models import Event, EventModerationMessage, EventMessage

    event = Event.get_event_or_404(event_id, request.user)
    moderation_messages = EventModerationMessage.get_event_messages(event)
    moderation_form = EventModerationMessageForm()
    event_messages = EventMessage.get_event_messages(event)
    messages_form = EventMessageForm()
    decision_form = DecisionForm(instance=event)

    return TemplateResponse(request, 'schedule/event.html', locals())


@login_required
@require_POST
def moderation_message(request, event_id):

    from apps.schedule.models import Event

    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventModerationMessageForm(request.POST)
    if form.is_valid():
        moderation_message = form.save(commit=False)
        moderation_message.event = event
        moderation_message.author = request.user
        moderation_message.save()

        messages.success(request, u"Wiadomość została wysłana")
        messages.info(request, u"Wiadomość została również wysłana emailem")

        return redirect(reverse('events:show', args=[str(event.id)]))

    raise Http404


@login_required
@require_POST
def message(request, event_id):
    from apps.schedule.models import Event

    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventMessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.event = event
        message.author = request.user

        message.save()

        messages.success(request, u"Wiadomość została wysłana")
        messages.info(request, u"Wiadomość została również wysłana emailem")

        return redirect(reverse('events:show', args=[str(event.id)]))

    raise Http404


@login_required
@require_POST
def change_interested(request, event_id):
    from apps.schedule.models import Event

    event = Event.get_event_or_404(event_id, request.user)
    if request.user in event.interested.all():
        event.interested.remove(request.user)
        messages.success(request, u'Nie obsereujesz już wydarzenia')
    else:
        event.interested.add(request.user)
        messages.success(request, u'Obserwujesz wydarzenie')

        return redirect(event)

    raise Http404


@login_required
@permission_required('schedule.manage_events')
def statistics(request):
    from apps.enrollment.courses.models import Course, Semester

    semester_id = request.GET.get('semester_id', None)
    semester = Semester.get_by_id_or_default(semester_id)

    exams = Course.get_courses_with_exam(semester).prefetch_related('teachers')

    return TemplateResponse(request, 'schedule/statistics.html', locals())


@login_required
def ajax_get_terms(request, year, month, day):
    from apps.enrollment.courses.models import Classroom

    time = datetime.date(int(year), int(month), int(day))
    terms = Classroom.get_terms_in_day(time, ajax=True)
    return HttpResponse(terms, mimetype="application/json")


class ClassroomTermsAjaxView(FullCalendarView):
    from apps.schedule.models import Term

    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(ClassroomTermsAjaxView, self).get_queryset()
        return queryset.filter(room__slug=self.kwargs['slug'])


class EventsTermsAjaxView(FullCalendarView):
    from apps.schedule.models import Term

    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(EventsTermsAjaxView, self).get_queryset()
        queryset = queryset.filter(event__type='2', event__visible=True)
        return queryset


class MyScheduleAjaxView(FullCalendarView):
    from apps.schedule.models import Term

    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        from apps.enrollment.courses.models import Group

        query = []

        if self.request.user.student:
            query.append(Q(record__student=self.request.user.student) & Q(record__status='1'))

        if self.request.user.employee:
            query.append(Q(teacher=self.request.user.employee))

        queryset = super(MyScheduleAjaxView, self).get_queryset()
        groups = Group.objects.filter(reduce(operator.or_, query))

        return queryset.filter(Q(event__group__in=groups) |
                               Q(event__interested=self.request.user) |
                               Q(event__author=self.request.user)).select_related('event', 'event__group',
                                                                                  'event__group__teacher')