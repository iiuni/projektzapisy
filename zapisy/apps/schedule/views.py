import datetime
import operator
import json
from functools import reduce
from itertools import groupby
from typing import List, NamedTuple, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term as CourseTerm
from apps.schedule.filters import EventFilter, ExamFilter
from apps.schedule.forms import (ConflictsForm, DecisionForm, EventForm, EventMessageForm,
                                 EventModerationMessageForm, EditTermFormSet, NewTermFormSet,
                                 ExtraTermsNumber)
from apps.schedule.models.event import Event
from apps.schedule.models.specialreservation import SpecialReservation
from apps.schedule.models.term import Term
from apps.schedule.utils import EventAdapter, get_week_range_by_date

from .forms import DoorChartForm, TableReportForm
from .fullcalendar import FullCalendarView
from .models.message import EventModerationMessage


@login_required
def classrooms(request):

    # Avoids lookup of non existing variable during template rendering
    room = None
    rooms = Classroom.get_in_institute(reservation=True)
    return TemplateResponse(request, 'schedule/classrooms.html', locals())


@login_required
def classroom(request, slug):

    rooms = Classroom.get_in_institute(reservation=True)
    try:
        room = Classroom.get_by_slug(slug)
    except ObjectDoesNotExist:
        raise Http404

    return TemplateResponse(request, 'schedule/classroom.html', locals())


@login_required
def new_reservation(request, event_id=None):
    if request.method == "POST":
        form = EventForm(request.user, request.POST)
        formset = NewTermFormSet(request.POST, form_kwargs={'user': request.user})
        if form.is_valid():
            event = form.save(commit=False)
            formset = NewTermFormSet(request.POST, instance=event, form_kwargs={'user': request.user})

            if formset.is_valid():
                event.save()
                formset.save()

                return redirect(event)
    else:
        form = EventForm(request.user)
        formset = NewTermFormSet(form_kwargs={'user': request.user})
    return render(request,
                  'schedule/reservation.html',
                  {'form': form, 'formset': formset, 'extra_terms_number': ExtraTermsNumber})


@login_required
def edit_reservation(request, event_id=None):
    is_edit = True
    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventForm(data=request.POST or None,
                     instance=event, user=request.user)
    formset = EditTermFormSet(request.POST or None, instance=event, form_kwargs={
                              'user': request.user})
    reservation = event.reservation

    if form.is_valid():
        event = form.save(commit=False)
        if not event.id:
            event.author = request.user
        event.reservation = reservation

        if formset.is_valid():
            event.save()
            formset.save()

            if Term.objects.filter(event=event).count() == 0:
                event.remove()
                messages.success(request, 'Usunięto wydarzenie')
                return reservations(request)

            messages.success(request, 'Zmieniono zdarzenie')
            return redirect(event)

    return TemplateResponse(request,
                            'schedule/reservation.html',
                            {'is_edit': is_edit,
                             'form': form,
                             'formset': formset,
                             'extra_terms_number': ExtraTermsNumber})


def session(request, semester=None):
    from apps.enrollment.courses.models.semester import Semester

    exams_filter = ExamFilter(request.GET, queryset=Term.get_exams())

    if semester:
        semester = Semester.get_by_id(semester)
    else:
        semester = Semester.get_current_semester()

    return TemplateResponse(request, 'schedule/session.html', {
        "semester": semester,
        "exams": exams_filter.qs
    })


@login_required
def reservations(request):
    events = EventFilter(request.GET, queryset=Event.get_all_without_courses())
    qs = Paginator(events.qs, 10).get_page(request.GET.get('page', 1))
    title = 'Zarządzaj rezerwacjami'
    return TemplateResponse(request, 'schedule/reservations.html', locals())


@login_required
@permission_required('schedule.manage_events')
def conflicts(request):
    """Finds conflicts in given daterange and pass into template.

    Implemented as 3D dictionary (ordered by day,classroom,hour).
    Works better than naive regroup in template (O(nlog(n)) vs O(n^2)).
    """
    form = ConflictsForm(request.GET)
    if form.is_valid():
        beg_date = form.cleaned_data['beg_date']
        end_date = form.cleaned_data['end_date']
    else:
        beg_date, end_date = get_week_range_by_date(datetime.datetime.today())

    terms = Term.prepare_conflict_dict(beg_date, end_date)
    title = 'Konflikty'
    return TemplateResponse(request, 'schedule/conflicts.html', locals())


@login_required
def history(request):
    events = EventFilter(request.GET, queryset=Event.get_for_user(request.user))
    qs = Paginator(events.qs, 10).get_page(request.GET.get('page', 1))
    title = 'Moje rezerwacje'
    return TemplateResponse(request, 'schedule/history.html', locals())


@login_required
@require_POST
@permission_required('schedule.manage_events')
def decision(request, event_id):
    event = Event.get_event_for_moderation_only_or_404(event_id, request.user)
    form = DecisionForm(request.POST, instance=event)
    event_status = event.status
    conflicts = event.get_conflicted()
    if conflicts:
        event.term_set.update(ignore_conflicts=True)

    if form.is_valid():
        if event_status == form.cleaned_data['status']:
            messages.error(request, "Status wydarzenia nie został zmieniony")
        else:
            event_obj = form.save()
            msg = EventModerationMessage()
            msg.author = request.user
            msg.message = "Status wydarzenia został zmieniony na " + \
                str(event_obj.get_status_display())
            msg.event = event_obj
            msg.save()
            messages.success(request, "Status wydarzenia został zmieniony")
            if event_obj.status == Event.STATUS_ACCEPTED:
                for conflict in conflicts:
                    messages.warning(request, "Powstał konflikt: " + conflict.title)
    else:
        messages.error(request, form.non_field_errors())

    return redirect(reverse('events:show', args=[str(event.id)]))


def events(request):
    return TemplateResponse(request, 'schedule/events.html', locals())


def event(request, event_id):
    from apps.schedule.models.message import EventModerationMessage, EventMessage

    event = Event.get_event_or_404(event_id, request.user)
    moderation_messages = EventModerationMessage.get_event_messages(event)
    event_messages = EventMessage.get_event_messages(event)

    return TemplateResponse(request, 'schedule/event.html', locals())


@login_required
@require_POST
def moderation_message(request, event_id):
    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventModerationMessageForm(request.POST)
    if form.is_valid():
        moderation_message = form.save(commit=False)
        moderation_message.event = event
        moderation_message.author = request.user
        moderation_message.save()

        messages.success(request, "Wiadomość została wysłana")
        messages.info(request, "Wiadomość została również wysłana emailem")

        return redirect(reverse('events:show', args=[str(event.id)]))

    raise Http404


@login_required
@require_POST
def message(request, event_id):
    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventMessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.event = event
        message.author = request.user

        message.save()

        messages.success(request, "Wiadomość została wysłana")
        messages.info(request, "Wiadomość została również wysłana emailem")

        return redirect(reverse('events:show', args=[str(event.id)]))

    raise Http404


@login_required
@require_POST
def change_interested(request, event_id):
    event = Event.get_event_or_404(event_id, request.user)
    if request.user in event.interested.all():
        event.interested.remove(request.user)
        messages.success(request, 'Nie obsereujesz już wydarzenia')
    else:
        event.interested.add(request.user)
        messages.success(request, 'Obserwujesz wydarzenie')

    return redirect(event)


@login_required
def get_terms(request, year, month, day):
    date = datetime.date(int(year), int(month), int(day))

    def make_dict(start_time, end_time):
        return {
            'begin': ':'.join(str(start_time).split(':')[:2]),
            'end': ':'.join(str(end_time).split(':')[:2])
        }

    result = {}

    rooms = Classroom.get_in_institute(reservation=True)

    for room in rooms:
        if room.number not in result:
            result[room.number] = {
                'id': room.id,
                'number': room.number,
                'capacity': room.capacity,
                'type': room.get_type_display(),
                'title': room.number,
                'occupied': []
            }

    terms = Term.objects.filter(day=date, room__in=rooms,
                                event__status='1').select_related('room', 'event')
    for term in terms:
        result[term.room.number]['occupied'].append(make_dict(term.start, term.end))

    # Some of the course terms fail to be represented by Event Terms which leads
    # to conflicts. Once this mess is fixed we can remove this lines below.
    semester = Semester.get_semester(date)
    if semester and semester.lectures_beginning <= date <= semester.lectures_ending:
        course_terms = CourseTerm.get_terms_for_semester(
            semester=semester, day=date, classrooms=rooms
        )
        for ct in course_terms:
            for room in ct.classrooms.all():
                result[room.number]['occupied'].append(make_dict(ct.start_time, ct.end_time))

    for key in result:
        array = sorted(result[key]['occupied'], key=lambda k: k['begin'])
        out = []
        for t in array:
            if out and out[-1]['begin'] <= t['begin'] <= out[-1]['end']:
                out[-1]['end'] = max(out[-1]['end'], t['end'])
            else:
                out.append(t)
        result[key]['occupied'] = out

    return HttpResponse(json.dumps(result), content_type="application/json")


class ClassroomTermsAjaxView(FullCalendarView):
    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(ClassroomTermsAjaxView, self).get_queryset()
        return queryset.filter(room__slug=self.kwargs['slug'])


class EventsTermsAjaxView(FullCalendarView):
    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        queryset = super(EventsTermsAjaxView, self).get_queryset()
        queryset = queryset.filter(event__type='2', event__visible=True)
        return queryset


class MyScheduleAjaxView(FullCalendarView):
    model = Term
    adapter = EventAdapter

    def get_queryset(self):
        from apps.enrollment.courses.models.group import Group

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


@login_required
@permission_required('schedule.manage_events')
def events_report(request):
    form_table = None
    form_doors = None
    if request.method == 'POST':
        # Pick the form that was sent.
        if request.POST['report-type'] == 'table':
            form = form_table = TableReportForm(request.POST)
            report_type = 'table'
        else:
            form = form_doors = DoorChartForm(request.POST)
            report_type = 'doors'
        if form.is_valid():
            return display_report(request, form, report_type)
    else:
        # Just display two forms.
        form_table = TableReportForm()
        form_doors = DoorChartForm()
    return render(request, 'schedule/reports/forms.html', {
        'form_table': form_table,
        'form_doors': form_doors,
    })


@login_required
@permission_required('schedule.manage_events')
def display_report(request, form, report_type: 'Literal["table", "doors"]'):  # noqa: F821
    class ListEvent(NamedTuple):
        date: Optional[datetime.datetime]
        weekday: int  # Monday is 1, Sunday is 7 like in
        # https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday.
        begin: datetime.time
        end: datetime.time
        room: Classroom
        title: str
        type: str
        author: str

    rooms = set(Classroom.objects.filter(id__in=form.cleaned_data['rooms']))
    events: List[ListEvent] = []
    # Every event will regardless of its origin be translated into a ListEvent.
    beg_date = form.cleaned_data.get('beg_date', None)
    end_date = form.cleaned_data.get('end_date', None)
    semester = None
    if form.cleaned_data.get('week', None) == 'currsem':
        semester = Semester.get_current_semester()
    elif form.cleaned_data.get('week', None) == 'nextsem':
        semester = Semester.objects.get_next()
    if semester:
        terms = CourseTerm.objects.filter(
            group__course__semester=semester, classrooms__in=rooms).distinct().select_related(
                'group__course', 'group__teacher',
                'group__teacher__user').prefetch_related('classrooms')
        for term in terms:
            for r in set(term.classrooms.all()) & rooms:
                events.append(
                    ListEvent(date=None,
                              weekday=int(term.dayOfWeek),
                              begin=term.start_time,
                              end=term.end_time,
                              room=r,
                              title=term.group.course.name,
                              type=term.group.human_readable_type(),
                              author=term.group.teacher.get_full_name()))
        terms = SpecialReservation.objects.filter(semester=semester, classroom__in=rooms).select_related('classroom')
        for term in terms:
            events.append(
                ListEvent(date=None,
                          weekday=int(term.dayOfWeek),
                          begin=term.start_time,
                          end=term.end_time,
                          room=term.classroom,
                          title=term.title,
                          type="",
                          author=""))
    elif 'week' in form.cleaned_data:
        beg_date = datetime.datetime.strptime(form.cleaned_data['week'], "%Y-%m-%d")
        end_date = beg_date + datetime.timedelta(days=6)
    if beg_date and end_date:
        terms = Term.objects.filter(day__gte=beg_date,
                                    day__lte=end_date,
                                    room__in=rooms,
                                    event__status=Event.STATUS_ACCEPTED).select_related(
                                        'room', 'event', 'event__group', 'event__author')
        for term in terms:
            events.append(
                ListEvent(date=term.day,
                          weekday=term.day.isoweekday(),
                          begin=term.start,
                          end=term.end,
                          room=term.room,
                          title=term.event.title or str(term.event.course) or "",
                          type=term.event.group.human_readable_type()
                          if term.event.group else term.event.get_type_display(),
                          author=term.event.author.get_full_name()))

    if report_type == 'table':
        events = sorted(events, key=operator.attrgetter('room.id', 'date', 'begin'))
    else:
        events = sorted(events, key=operator.attrgetter('room.id', 'weekday', 'begin'))
    terms_by_room = groupby(events, operator.attrgetter('room.number'))
    terms_by_room = sorted([(int(k), list(g)) for k, g in terms_by_room])

    return render(request, f'schedule/reports/report_{report_type}.html', {
        'events': terms_by_room,
        'semester': semester,
        'beg_date': beg_date,
        'end_date': end_date,
    })
