import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
import operator
from apps.enrollment.courses.models.classroom import Classroom
from apps.schedule.models.event import Event
from apps.schedule.models.term import Term
from apps.schedule.filters import EventFilter, ExamFilter
from apps.schedule.forms import EventForm, TermFormSet, DecisionForm, \
    EventModerationMessageForm, EventMessageForm, ConflictsForm
from apps.schedule.utils import EventAdapter, get_week_range_by_date
from apps.utils.fullcalendar import FullCalendarView
from apps.users.models import BaseUser

from xhtml2pdf import pisa
import io
from functools import reduce


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
def reservation(request, event_id=None):
    form = EventForm(data=request.POST or None, user=request.user)

    if form.is_valid():
        event = form.save(commit=False)
        event.author = request.user
        formset = TermFormSet(request.POST or None, instance=event)
        if formset.is_valid():
            event.save()
            formset.save()

            return redirect(event)
        errors = True
    else:
        formset = TermFormSet(data=request.POST or None, instance=Event())

    return TemplateResponse(request, 'schedule/reservation.html', locals())


@login_required
def edit_event(request, event_id=None):
    is_edit = True
    event = Event.get_event_for_moderation_or_404(event_id, request.user)
    form = EventForm(data=request.POST or None, instance=event, user=request.user)
    formset = TermFormSet(request.POST or None, instance=event)
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
    errors = True

    return TemplateResponse(request, 'schedule/reservation.html', locals())


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
    """
    Finds conflicts in given daterange and pass into template.
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
def decision(request, event_id):
    from .models.message import EventModerationMessage

    event = Event.get_event_for_moderation_only_or_404(event_id, request.user)

    form = DecisionForm(request.POST, instance=event)

    event_status = event.status

    if form.is_valid():
        if event_status == form.cleaned_data['status']:
            messages.error(request, 'Status wydarzenia nie został zmieniony')
        else:
            event_obj = form.save()
            msg = EventModerationMessage()
            msg.author = request.user
            msg.message = 'Status wydarzenia został zmieniony na ' + \
                str(event_obj.get_status_display())
            msg.event = event_obj
            msg.save()
            messages.success(request, 'Status wydarzenia został zmieniony')

    return redirect(reverse('events:show', args=[str(event.id)]))


def events(request):
    return TemplateResponse(request, 'schedule/events.html', locals())


def event(request, event_id):
    from apps.schedule.models.message import EventModerationMessage, EventMessage

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

    raise Http404


@login_required
@permission_required('schedule.manage_events')
def statistics(request):
    from apps.enrollment.courses.models.course import Course
    from apps.enrollment.courses.models.semester import Semester

    semester_id = request.GET.get('semester_id', None)
    semester = Semester.get_by_id_or_default(semester_id)

    exams = Course.get_courses_with_exam(semester).select_related('entity', 'entity__owner')

    return TemplateResponse(request, 'schedule/statistics.html', locals())


@login_required
def ajax_get_terms(request, year, month, day):
    from apps.enrollment.courses.models.classroom import Classroom

    time = datetime.date(int(year), int(month), int(day))
    terms = Classroom.get_terms_in_day(time, ajax=True)
    return HttpResponse(terms, content_type="application/json")


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

        if BaseUser.is_student(self.request.user):
            query.append(Q(record__student=self.request.user.student) & Q(record__status='1'))

        if BaseUser.is_employee(self.request.user):
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
    from .forms import ReportForm
    if request.method == 'POST':
        form = ReportForm(request.POST)
        form.fields["rooms"].choices = [(x.pk, x.number)
                                        for x in Classroom.get_in_institute(reservation=True)]
        if form.is_valid():
            beg_date = form.cleaned_data["beg_date"]
            end_date = form.cleaned_data["end_date"]
            rooms = form.cleaned_data["rooms"]
            return events_raport_pdf(request, beg_date, end_date, rooms)
    else:
        form = ReportForm()
        form.fields["rooms"].choices = [(x.pk, x.number)
                                        for x in Classroom.get_in_institute(reservation=True)]
    return TemplateResponse(request, 'schedule/events_report.html', locals())


@login_required
@permission_required('schedule.manage_events')
def events_raport_pdf(request, beg_date, end_date, rooms):

    events = []
    # we are using this function for sorting
    for room in rooms:
        try:
            cr = Classroom.objects.get(id=room)
        except ObjectDoesNotExist:
            raise Http404
        # probably not safe
        events.append((cr, Term.objects.filter(
            day__gte=beg_date,
            day__lte=end_date,
            room=room,
            event__status=Event.STATUS_ACCEPTED,
        ).order_by('day', 'start')))

    context = {
        'beg_date': beg_date,
        'end_date': end_date,
        'events': events,
        'pagesize': 'A4',
        'report': True
    }

    template = get_template('schedule/events_report_pdf.html')
    html = template.render(context)
    result = io.BytesIO()

    pisa.pisaDocument(io.StringIO(html), result, encoding='UTF-8')

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=raport.pdf'

    return response
