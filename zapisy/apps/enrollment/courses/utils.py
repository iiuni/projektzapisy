# -*- coding: utf-8 -*-
import json

def prepare_group_data(course, student):
    from apps.enrollment.records.models import Queue, Record
    groups = course.groups.all()
    queued = Queue.queued.filter(group__course=course, student=student, deleted=False)
    enrolled_ids = Record.enrolled.filter(group__course=course,
        student=student).values_list('group__id', flat=True)
    queued_ids = queued.values_list('group__id', flat=True)
    pinned_ids = Record.pinned.filter(group__course=course,
        student=student).values_list('group__id', flat=True)
    queue_priorities = Queue.queue_priorities_map(queued)

    data = {}
    for group in groups:
        data[group.id] = json.dumps(group.serialize_for_json(
            enrolled_ids, queued_ids, pinned_ids,
            queue_priorities, student))
    return data
