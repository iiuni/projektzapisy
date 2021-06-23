import copy
import json
from collections import defaultdict
from operator import attrgetter, itemgetter
from datetime import datetime, timedelta
from itertools import groupby
from typing import Literal, NamedTuple, Optional, List, Dict, Set, Tuple

from django.http.request import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render
from django.core.validators import ValidationError
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.schedule.forms import DoorChartForm, TableReportForm
from apps.schedule.models.term import Term
from apps.schedule.models.event import Event
from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.term import Term as CourseTerm
from apps.users.models import Student, is_employee, is_student


@login_required
def calendar(request):
    rooms = Classroom.get_in_institute(reservation=True)
    new_rooms = [{"number": r.number,
                  "capacity": r.capacity,
                  "type": r.get_type_display()} for r in rooms]
    numeric = sorted([r for r in new_rooms if r["number"].isdigit()], key=lambda r: int(r["number"]))
    alpha = sorted([r for r in new_rooms if not r["number"].isdigit()], key=itemgetter("number"))
    numeric.extend(alpha)
    return render(request, 'schedule/calendar.html', {"new_rooms": numeric,
                                                      "user_info": {
                                                          "full_name": request.user.get_full_name(),
                                                          "is_student": is_student(request.user),
                                                          "is_employee": is_employee(request.user),
                                                          "is_admin": request.user.has_perm('schedule.manage_events')}})


def chosen_days_terms(request: HttpRequest) -> JsonResponse:
    """Returns a mapping from room number to an array of time intervals when it is reserved."""
    day = request.GET.get('days')
    event = request.GET.get('event', None)
    try:
        day = datetime.strptime(day, '%Y-%m-%d')
    except ValueError:
        return HttpResponseBadRequest('Jedna z przesłanych dat jest złego formatu.')

    # TODO Should we also display STATUS_PENDING events?
    terms = Term.objects.filter(
        day=day, room__isnull=False, room__can_reserve=True,
        event__status=Event.STATUS_ACCEPTED
    ).select_related('room')
    if event is not None:
        terms = terms.exclude(event__pk=event)
    payload = defaultdict(list)
    for term in terms:
        pr = payload[term.room.number]
        if pr and pr[-1][1] > term.start:
            # Last term overlaps with the current.
            start, _ = pr.pop()
            pr.append((start, term.end))
        else:
            pr.append((term.start, term.end))
    return JsonResponse({k: [(s.isoformat(timespec='minutes'), e.isoformat(timespec='minutes')) for s, e in l]
                         for k, l in payload.items()})


def _check_and_prepare_get_data(request, require_dates: bool = True):
    """Parse GET query parameters to python objects.

    Args:
        request: GET request.
        require_dates: Can omit dates - 'start' and 'end' in request parameters.

    Returns:
        Dict with parsed and validated python objects needed to filter Terms.

    Raises:
        ValidationError: Missing or incorrect request parameters like wrong
          date format or nonexistent Event status and type.
    """
    data = {}
    if require_dates:
        try:
            data['start'] = datetime.strptime(request.GET.get('start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            data['end'] = datetime.strptime(request.GET.get('end'), '%Y-%m-%dT%H:%M:%S.%fZ')
        except KeyError:
            raise ValidationError('Nie przesłano dat początku i końcu termów.')
        except ValueError:
            raise ValidationError('Przesłane daty są złego formatu.')
    try:
        types = request.GET.get('types', [])
        types = types.split(',') if isinstance(types, str) else types
        for type_ in types:
            if not any(type_ == t for t, _ in Event.TYPES):
                raise ValueError
        data['types'] = types
    except ValueError:
        raise ValidationError('Przesłane typy wydarzeń są nieprawidłowe.')
    try:
        statuses = request.GET.get('statuses', [])
        statuses = statuses.split(',') if isinstance(statuses, str) else statuses
        for status in statuses:
            if not any(status == s for s, _ in Event.STATUSES):
                raise ValueError
        data['statuses'] = statuses
    except ValueError:
        raise ValidationError('Przesłane statusy wydarzeń są nieprawidłowe.')
    try:
        data['page'] = int(request.GET.get('page', 1))
        visible = request.GET.get('visible', None)
        data['visible'] = bool(visible) if visible is not None else None
        ignore_conflicts = request.GET.get('ignore_conflicts', None)
        data['ignore_conflicts'] = bool(ignore_conflicts) if ignore_conflicts is not None else None
        data['title_or_author'] = str(request.GET.get('title_author', ''))
        rooms = request.GET.get('rooms', [])
        data['rooms'] = rooms.split(',') if rooms else rooms
    except ValueError as err:
        raise ValidationError(err)
    return data


@login_required
def terms(request) -> JsonResponse:
    """Returns Terms info needed for fullcalendar event fetching.

    Args:
        request - GET request sent from fullcalendar.

    Returns:
        JsonResponse with List of Dicts. Single Dict contains info about
        single term to display in fullcalendar. Single term here contains
        info from Event too: title, status, type etc.
    """
    try:
        data = _check_and_prepare_get_data(request)
    except ValidationError as err:
        return HttpResponseBadRequest(err)
    query = Term.objects.order_by().filter(day__range=[data['start'],
                                                       data['end']]).select_related('event', 'event__author')
    if data['rooms']:
        query = query.filter(room__number__in=data['rooms'])
    if data['types']:
        query = query.filter(event__type__in=data['types'])
    if data['statuses']:
        query = query.filter(event__status__in=data['statuses'])
    if data['title_or_author']:
        filter_words = data['title_or_author'].split()
        for word in filter_words:
            query = query.filter(Q(event__title__icontains=word) |
                                 Q(event__author__first_name__icontains=word) |
                                 Q(event__author__last_name__icontains=word))
    if data['visible'] is not None:
        query = query.filter(event__visible=data['visible'])
    if data['ignore_conflicts'] is not None:
        query = query.filter(ignore_conflicts=data['ignore_conflicts'])
    query = query.distinct('event', 'day', 'start', 'end')
    payload = []
    for term in query:
        event = term.event
        if not event.can_user_see(request.user):
            continue
        payload.append({"title": event.title,
                        "status": event.status,
                        "type": event.type,
                        "visible": event.visible,
                        "ignore_conflicts": term.ignore_conflicts,
                        "url": event.get_absolute_url(),
                        "user_is_author": request.user == event.author,
                        "start": datetime.combine(term.day, term.start).isoformat(),
                        "end": datetime.combine(term.day, term.end).isoformat()})
    return JsonResponse(payload, safe=False)


def _get_author_name_and_url(author: User, logged_user: User
                             ) -> Tuple[str or None, str or None]:
    """Returns tuple with event author full name and url to author in users app.

    Checks if event author is student or employee. If event author is student
    with hidden name and logged user is not employee, don't return author
    details.
    """
    if not author:
        return None, None
    if is_employee(author):
        author_url = reverse('employee-profile', args=[author.pk])
    else:
        author_url = reverse('student-profile', args=[author.pk])
        student = Student.objects.get(user=author)
        if not student.consent_granted() and not logged_user.employee:
            return "Student ukryty", None
    return author.get_full_name(), author_url


def _get_validated_terms(payload: Dict[str, str or List[Dict]], event: Event = None) -> List[Term]:
    """Returns list of validated Terms created from given payload.

    Payload has terms info to create, but terms that differ only in room number
    are sent as single term with 'rooms' key. This function creates
    (but not saves) separate Term for every room as stored in database.
    Checks if created Terms do not collide with themselves,

    Args:
        payload: Converted JSON from POST request body.
        event: Create every Term with this Event.

    Raises:
        ValidationError: When any term from payload miss required keys or has
          incorrect value like wrong date format. Also when created Term
          validation failed like nonexistent room.
    """
    payload_terms = payload.get('terms', [])
    if not payload_terms:
        raise ValidationError("Missing terms key in payload.")
    rooms_to_query = set()
    for payload_term in payload_terms:
        if 'rooms' in payload_term and payload_term['rooms']:
            for room in payload_term['rooms']:
                rooms_to_query.add(room)
    rooms = {room.number: room for room in Classroom.objects.filter(number__in=rooms_to_query)}
    terms = []
    try:
        for payload_term in payload_terms:
            term = Term(event=event,
                        start=datetime.strptime(payload_term['start'], '%H:%M').time(),
                        end=datetime.strptime(payload_term['end'], '%H:%M').time(),
                        day=datetime.strptime(payload_term['day'], '%Y-%m-%d').date())
            if 'rooms' in payload_term and payload_term['rooms']:
                for number, ignore_conflicts in payload_term['rooms'].items():
                    term.room = rooms[number]
                    term.place = None
                    term.ignore_conflicts = ignore_conflicts
                    term.clean()
                    terms.append(term)
                    term = copy.deepcopy(term)
            if 'place' in payload_term and payload_term['place']:
                term.room = None
                term.place = payload_term['place']
                term.clean()
                terms.append(term)
        if not terms:
            raise ValueError("There are no terms sent in payload.")
        if any(t_x.room == t_y.room and t_x.day == t_y.day and t_x.start < t_y.end and t_x.end > t_y.start and
               t_x.room and t_y.room and t_x != t_y for t_x in terms for t_y in terms):
            raise ValidationError("Created Terms collide with themselves.")
        return terms
    except (ValueError, TypeError, ObjectDoesNotExist) as err:
        raise ValidationError(err)
    except KeyError as err:
        raise ValidationError("Missing required term key: " + str(err))


def _check_conflicts(terms: List[Term], ignore_terms: List[Term] = []) -> Set[Term]:
    """Checks if given Terms make conflicts with other Terms in database.

    Args:
        terms: Terms to check if conflicts exists.
        ignore_terms: Ignore conflicts with these Terms.

    Returns:
        Terms that make collisions with given Terms.
    """
    conflicts_terms = set()
    for term in terms:
        if term.ignore_conflicts:
            continue
        temp_conflicts = term.get_conflicted_except_given_terms(ignore_terms)
        for conflict in temp_conflicts:
            conflicts_terms.add(conflict)
    return conflicts_terms


def _send_conflicts(conflicts: Set[Term], status: int = 200) -> JsonResponse:
    """Returns JsonResponse with proper conflicts structure and status.

    Args:
        conflicts: Terms that make conflicts with other Terms.
        status: status of JsonResponse.

    Returns:
        JsonResponse with List of proper conflicts Dict for frontend. Single
        conflict contains information about colliding Term and Event.
    """
    payload = []
    for term in conflicts:
        payload.append({"title": term.event.title,
                        "description": term.event.description,
                        "status": term.event.status,
                        "type": term.event.type,
                        "visible": term.event.visible,
                        "url": term.event.get_absolute_url(),
                        "start": term.start,
                        "end": term.end,
                        "day": term.day,
                        "room": term.room.number if term.room else None,
                        "place": term.place})
    return JsonResponse(payload, safe=False, status=status)


@login_required
@require_POST
def check_conflicts(request, event_id: int or None = None) -> JsonResponse:
    """Sends JsonResponse with conflicts list.

    Checks for collisions with retrieved Terms from request payload and sends
    those collisions.

    Args:
        request: POST request. This function retrieves Terms from request body
          to check their conflicts.
        event_id: Id of Event which Terms will be ignored when checking
          conflicts.

    Returns:
        JsonResponse with List of conflicts Dict for frontend, this List may be
        empty. See _send_conflicts for conflict Dict structure.
    """
    payload = json.loads(request.body)
    try:
        if event_id:
            event = Event.objects.get(id=event_id)
            conflicts = _check_conflicts(_get_validated_terms(payload),
                                         ignore_terms=event.term_set.all().select_related('room'))
        else:
            conflicts = _check_conflicts(_get_validated_terms(payload))
    except (ValidationError, ObjectDoesNotExist) as err:
        return HttpResponseBadRequest(err)
    return _send_conflicts(conflicts, status=200)


def _group_terms_same_date_and_time(terms: List[Term]) -> List[Dict]:
    """Group Terms that occur at same date and time.

    Terms that differ only in room number are grouped as single term Dict
    with 'rooms' key. If Terms differ only in place, create separate term Dicts.

    Returns:
        List of Dict with proper Term info and structure for frontend.
    """
    grouped_terms = []
    for term in terms:
        insert_to_grouped_terms = True
        for grouped_term in grouped_terms:
            if term.start == grouped_term["start"] and term.end == grouped_term["end"] \
                    and term.day == grouped_term["day"]:
                if term.place and grouped_term["place"]:
                    break
                if term.place and not grouped_term["place"]:
                    grouped_term["place"] = term.place
                    insert_to_grouped_terms = False
                    break
                grouped_term["rooms"][term.room.number] = term.ignore_conflicts
                insert_to_grouped_terms = False
                break
        if insert_to_grouped_terms:
            grouped_terms.append({
                "start": term.start,
                "end": term.end,
                "day": term.day,
                "rooms": {term.room.number: term.ignore_conflicts} if term.room else {},
                "place": term.place})
    return grouped_terms


def _get_event_info_to_send(event: Event, user: User) -> Dict[str, str or List[Dict]]:
    """Returns Dict with all needed info from Event for frontend.

    Example usage is when client clicked single event in fullcalendar.
    """
    terms = event.term_set.all().select_related('room')
    author_full_name, author_url = _get_author_name_and_url(event.author, user)
    return {"terms": _group_terms_same_date_and_time(terms),
            "description": event.description,
            "author": author_full_name,
            "author_url": author_url,
            "user_is_author": user == event.author,
            "title": event.title,
            "status": event.status,
            "type": event.type,
            "visible": event.visible,
            "created": event.created,
            "edited": event.edited,
            "url": event.get_absolute_url(),
            "id": event.pk,
            }


@transaction.atomic
def create_event(request) -> JsonResponse:
    """Create Event with request payload properties.

    Before creating, Event and Terms are validated.

    Args:
        request: POST request.

    Returns:
        JsonResponse with created Event data.
    """
    payload = json.loads(request.body)
    event = Event()
    event.title = payload.get('title', '')
    event.author = request.user
    event.description = payload.get('description', '')
    event.visible = payload.get('visible', True)
    event.status = payload.get('status', Event.STATUS_PENDING)
    event.type = payload.get('type', Event.TYPE_GENERIC)
    try:
        event.clean()
        event.save()
        terms = _get_validated_terms(payload, event=event)
        conflicts = _check_conflicts(terms)
    except ValidationError as err:
        transaction.set_rollback(True)
        if hasattr(err, 'code') and err.code == 'permission':
            return HttpResponseForbidden(err)
        return HttpResponseBadRequest(err)
    if conflicts and event.status != Event.STATUS_REJECTED:
        conflicts = _send_conflicts(conflicts, status=400)
        transaction.set_rollback(True)
        return conflicts
    for term in terms:
        term.save()
    return JsonResponse(_get_event_info_to_send(event, request.user), status=201)


@transaction.atomic
def update_event(request, event_id: int) -> JsonResponse:
    """Update Event with request payload properties.

    Before updating, Event and Terms are validated. Replaces all existing Terms
    with new created Terms from sent payload.

    Args:
        request: POST request.
        event_id: Updating Event id.

    Returns:
        JsonResponse with updated Event data.
    """
    payload = json.loads(request.body)
    try:
        event = Event.get_event_or_404(event_id, request.user)
        current_author = event.author
        event.author = request.user
        event.title = payload.get('title', '')
        event.description = payload.get('description', '')
        event.visible = payload.get('visible', True)
        event.status = payload.get('status', Event.STATUS_PENDING)
        event.type = payload.get('type', Event.TYPE_GENERIC)
        event.clean()
        event.author = current_author
        event.save()
        new_terms = _get_validated_terms(payload, event=event)
        present_terms = event.term_set.all().select_related('room')
        conflicts = _check_conflicts(new_terms, ignore_terms=present_terms)
    except ValidationError as err:
        transaction.set_rollback(True)
        if hasattr(err, 'code') and err.code == 'permission':
            return HttpResponseForbidden(err)
        return HttpResponseBadRequest(err)
    if conflicts and event.status != Event.STATUS_REJECTED:
        conflicts = _send_conflicts(conflicts, status=400)
        transaction.set_rollback(True)
        return conflicts
    for present_term in present_terms:
        present_term.delete()
    for new_term in new_terms:
        new_term.save()
    return JsonResponse(_get_event_info_to_send(event, request.user), status=201)


@login_required
def events(request) -> JsonResponse:
    """Retrieve many Events or create single Event.

    When request method is GET, get sent query parameters and filter Events.
    Send only these Events that can be seen by a user. When request method is
    POST, validate if user can create Event with sent JSON properties and
    create Event.

    Args:
        request: GET or POST request.

    Returns:
        JsonResponse with retrieved Events and Terms or created Event and Terms.
    """
    if request.method == "POST":
        return create_event(request)
    try:
        data = _check_and_prepare_get_data(request, require_dates=False)
    except ValidationError as err:
        return HttpResponseBadRequest(err)
    query = Event.objects.filter().select_related('author')
    if data['types']:
        query = query.filter(type__in=data['types'])
    if data['statuses']:
        query = query.filter(status__in=data['statuses'])
    if data['title_or_author']:
        query_words = data['title_or_author'].split()
        for word in query_words:
            query = query.filter(
                Q(title__icontains=word) |
                Q(author__first_name__icontains=word) |
                Q(author__last_name__icontains=word)
            )
    query = query.filter(visible=data['visible'])
    query = query.order_by('-created')
    query = Paginator(query, 20).get_page(data['page'])
    payload = []
    for event in query:
        if not event.can_user_see(request.user):
            continue
        payload.append(_get_event_info_to_send(event, request.user))
    return JsonResponse(payload, safe=False)


@login_required
@require_POST
@transaction.atomic
def delete_event(request, event_id: int) -> HttpResponse:
    """Delete Event after authorizing user.

    Args:
        request: POST request.
        event_id: Event Id to delete.
    """
    event = Event.get_event_or_404(event_id, request.user)
    if not request.user.has_perm('schedule.manage_events') and event.author != request.user:
        return HttpResponseForbidden('Nie można usuwać wydarzeń nie będąc ich autorem')
    event.delete()
    return HttpResponse("Usunięto wydarzenie", status=200)


@login_required
def event(request, event_id: int) -> JsonResponse:
    """Retrieve single Event or update single Event.

    When request method is GET, send single Event info if logged user can see
    this event. When request method is POST, validate if user can update Event
    with sent JSON properties and update Event.

    Args:
        request: GET or POST request.
        event_id: Event ID to retrieve or update.

    Returns:
        JsonResponse with retrieved Event and Terms or updated Event and Terms.
    """
    if request.method == "POST":
        return update_event(request, event_id)
    event = Event.get_event_or_404(event_id, request.user)
    return JsonResponse(_get_event_info_to_send(event, request.user))


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
        date: Optional[datetime]
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
        semester = Semester.get_upcoming_semester()
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
                              type=term.group.get_type_display(),
                              author=term.group.teacher.get_full_name()))
        special_reservation_events = Event.objects.filter(type=Event.TYPE_SPECIAL_RESERVATION)
        semester_start_day = semester.semester_beginning
        semester_end_day = semester.semester_ending
        terms = []
        # Special reservations have same room, start and end every week.
        # Do not duplicate those terms
        for event in special_reservation_events:
            same_room_hour_terms = set()
            temp_terms = event.term_set.all()
            for term in temp_terms:
                if semester_start_day <= term.day <= semester_end_day and term.room in rooms \
                        and (term.room, term.start, term.end) not in same_room_hour_terms:
                    same_room_hour_terms.add((term.room, term.start, term.end))
                    terms.append(term)
        for term in terms:
            events.append(
                ListEvent(date=None,
                          weekday=term.day.isoweekday(),
                          begin=term.start,
                          end=term.end,
                          room=term.room,
                          title=term.event.title,
                          type="",
                          author=""))
    elif 'week' in form.cleaned_data:
        beg_date = datetime.strptime(form.cleaned_data['week'], "%Y-%m-%d")
        end_date = beg_date + timedelta(days=6)
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
                          type=term.event.group.get_type_display()
                          if term.event.group else term.event.get_type_display(),
                          author=term.event.author.get_full_name()))
    if report_type == 'table':
        events = sorted(events, key=attrgetter('room.id', 'date', 'begin'))
    else:
        events = sorted(events, key=attrgetter('room.id', 'weekday', 'begin'))
    terms_by_room = groupby(events, attrgetter('room.number'))
    terms_by_room = sorted([(int(k), list(g)) for k, g in terms_by_room])

    return render(request, f'schedule/reports/report_{report_type}.html', {
        'events': terms_by_room,
        'semester': semester,
        'beg_date': beg_date,
        'end_date': end_date,
    })
