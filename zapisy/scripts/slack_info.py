
from django.core.exceptions import ObjectDoesNotExist
from apps.users.models import Student
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models import Course, CourseEntity, Semester
from apps.enrollment.records.models import Record,Queue
import json
import requests

def run():
    gg = Group.objects.filter(course__semester_id=Semester.objects.get_next().id)
    bad_groups=[]
    for g in gg:
        if len(Record.get_students_in_group(g)) != g.enrolled:
            bad_groups.append(g)

    for g in gg:
        if len(Queue.get_students_in_queue(g)) != g.queued:
            bad_groups.append(g)
            print(g.id, len(Queue.get_students_in_queue(g)), g.queued)

    s = ''
    for g in bad_groups:
        s += '<https://zapisy.ii.uni.wroc.pl/records/'+str(g.id)+'/records|' + str(g) + '>\n Enrolled_real/Enrolled: ' + str(len(Record.get_students_in_group(g))) + '/' + str(g.enrolled) + '\n Queued_real/Queued: ' + str(len(Queue.get_students_in_queue(g))) + '/' + str(g.queued) + "\n"

    webhook_url = 'https://hooks.slack.com/services/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'
    slack_data = {'text': "Wrong group numbers:\n\n"+s}

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )