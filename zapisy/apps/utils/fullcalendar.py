import datetime
import json

from django import http
from django.db.models import Q
from django.http import Http404
from django.views.generic.list import BaseListView


class FullCalendarAdapter(object):
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request

    def collection_as_json(self):
        result = []

        for item in self.queryset:
            result.append(self.item_as_json(item))

        return json.dumps(result)

    def item_as_json(self, item):
        result = {}

        id = self.get_id(item)
        title = self.get_title(item)
        allDay = self.get_allDay(item)
        start = self.get_start(item)
        end = self.get_end(item)
        description = self.get_description(item)
        url = self.get_url(item)
        className = self.get_className(item)
        editable = self.get_editable(item)
        color = self.get_color(item)
        backgroundColor = self.get_backgroundColor(item)
        borderColor = self.get_borderColor(item)
        textColor = self.get_textColor(item)

        if id is not None:
            result['id'] = id

        if title is not None:
            result['title'] = title

        if allDay is not None:
            result['allDay'] = allDay

        if start is not None:
            result['start'] = start

        if end is not None:
            result['end'] = end

        if description is not None:
            result['description'] = description

        if url is not None:
            result['url'] = url

        if className is not None:
            result['className'] = className

        if editable is not None:
            result['editable'] = editable

        if color is not None:
            result['color'] = color

        if backgroundColor is not None:
            result['backgroundColor'] = backgroundColor

        if borderColor is not None:
            result['borderColor'] = borderColor

        if textColor is not None:
            result['textColor'] = textColor

        return result

    def get_id(self, item):
        """
        String/Integer. Optional

        Uniquely identifies the given event. Different instances of repeating events
        should all have the same id.
        """
        return item.event_id

    def get_title(self, item):
        """
        String. Required.

        The text on an event's element
        """
        return item.event.title

    def get_allDay(self, item):
        """
        true or false. Optional.

        Whether an event occurs at a specific time-of-day. This property affects whether
        an event's time is shown. Also, in the agenda views, determines if it is displayed
        in the "all-day" section. If this value is not explicitly specified, allDayDefault
        will be used if it is defined. If all else fails, FullCalendar will try to guess.
        If either the start or end value has a "T" as part of the ISO8601 date string,
        allDay will become false. Otherwise, it will be true. Don't include quotes around
        your true/false. This value is a boolean, not a string!
        """
        return False

    def get_start(self, item):
        """
        The date/time an event begins. Required.

        A Moment-ish input, like an ISO8601 string. Throughout the API this will become
        a real Moment object.
        """
        return datetime.datetime.combine(item.day, item.start).isoformat()

    def get_end(self, item):
        """
        The exclusive date/time an event ends. Optional.

        A Moment-ish input, like an ISO8601 string. Throughout the API this will become
        a real Moment object. It is the moment immediately after the event has ended.
        For example, if the last full day of an event is Thursday, the exclusive end
        of the event will be 00:00:00 on Friday!
        """
        return datetime.datetime.combine(item.day, item.end).isoformat()

    def get_description(self, item):
        return item.event.description

    def get_url(self, item):
        """
        String. Optional.

        A URL that will be visited when this event is clicked by the user.
        For more information on controlling this behavior, see the eventClick callback.
        """
        return item.event.get_absolute_url()

    def get_className(self, item):
        """
        String/Array. Optional.

        A CSS class (or array of classes) that will be attached to this event's element.
        """
        return None

    def get_editable(self, item):
        """
        true or false. Optional.

        Overrides the master editable option for this single event.
        """
        return False

    def get_color(self, item):
        """
        Sets an event's background and border color just like the calendar-wide eventColor option.
        """
        return None

    def get_backgroundColor(self, item):
        """
        Sets an event's background color just like the calendar-wide eventBackgroundColor option.
        """
        return None

    def get_borderColor(self, item):
        """
        Sets an event's border color just like the the calendar-wide eventBorderColor option.
        """
        return None

    def get_textColor(self, item):
        """
        Sets an event's text color just like the calendar-wide eventTextColor option.
        """
        return None


class FullCalendarView(BaseListView):

    adapter = FullCalendarAdapter

    def get_queryset(self):

        if 'start' not in self.request.GET or 'end' not in self.request.GET:
            raise Http404

        start = self.request.GET.get('start')
        if 'T' in start:
            start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        else:
            start = datetime.datetime.strptime(start, "%Y-%m-%d")

        end = self.request.GET.get('end')
        if 'T' in end:
            end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        else:
            end = datetime.datetime.strptime(end, "%Y-%m-%d")

        # 3.7
        # start = datetime.datetime.fromisoformat(self.request.GET.get('start'))
        # end = datetime.datetime.fromisoformat(self.request.GET.get('end'))

        if not self.queryset:
            self.queryset = super(FullCalendarView, self).get_queryset()

        return self.queryset.filter(Q(day__gte=start), Q(day__lt=end)).select_related('event')

    def render_to_response(self, context):
        return self.get_json_response(self.convert_to_json(context['object_list']))

    def get_json_response(self, content, **kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **kwargs)

    def convert_to_json(self, queryset):
        return self.adapter(queryset, self.request).collection_as_json()
