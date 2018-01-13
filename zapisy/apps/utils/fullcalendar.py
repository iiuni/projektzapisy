# -*- coding: utf-8 -*-
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

        Uniquely identifies the given event. Different instances of repeating events should all have the same id.
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
        an event's time is shown. Also, in the agenda views, determines
        if it is displayed in the "all-day" section.

        When specifying Event Objects for events or eventSources, omitting
         his property will make it inherit from allDayDefault, which is normally true.
        """
        return False

    def get_start(self, item):
        """The date/time an event begins.

        When specifying Event Objects for events or eventSources, you may
        specify a string in IETF format (ex: "Wed, 18 Oct 2009 13:00:00 EST"),
        a string in ISO8601 format (ex: "2009-11-05T13:15:30Z") or a UNIX
        timestamp.
        """
        import time
        return time.mktime(
            datetime.datetime.combine(item.day, item.start).timetuple())

    def get_end(self, item):
        """The date/time an event ends.

        As with start, you may specify it in IETF, ISO8601, or UNIX timestamp
        format. If an event is all-day the end date is inclusive. This means an
        event with start Nov 10 and end Nov 12 will span 3 days on the
        calendar. If an event is NOT all-day the end date is exclusive. This is
        only a gotcha when your end has time 00:00. It means your event ends on
        midnight, and it will not span through the next day.

        """
        import time
        return time.mktime(
            datetime.datetime.combine(item.day, item.end).timetuple())

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

        if 'start' in self.request.GET or not 'end' not in self.request.GET:
            raise Http404

        start = datetime.datetime.fromtimestamp(
            int(self.request.GET.get('start')))
        end = datetime.datetime.fromtimestamp(int(self.request.GET.get('end')))

        if not self.queryset:
            self.queryset = super(FullCalendarView, self).get_queryset()

        return self.queryset.filter(Q(day__gte=start), Q(day__lte=end)).select_related('event')

    def render_to_response(self, context):
        return self.get_json_response(self.convert_to_json(context['object_list']))

    def get_json_response(self, content, **kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **kwargs)

    def convert_to_json(self, queryset):
        return self.adapter(queryset, self.request).collection_as_json()
