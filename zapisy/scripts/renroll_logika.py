from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models import Course, CourseEntity
from apps.offer.vote.models import SystemState
from apps.offer.vote.models.single_vote import SingleVote
from apps.enrollment.records.models import Record
import math

def run():
    groupA_id = 13773
    groupsB_ids = [13785,13786,13787,13788]
    studA = Record.get_students_in_group(groupA_id)
    chunk_size = int(math.ceil(1.0*len(studA)/len(groupsB_ids)))
    for i, gB_id in enumerate(groupsB_ids):
        studs = studA[i*chunk_size:(i+1)*chunk_size]
        g = Group.objects.get(id=gB_id)
        print(len(studs))
        for s in studs:
            print(s)
            pass
            #g.enroll_student(s)

g = Group.objects.get(id=gB_id)
for i in rr[0:20]:
    g.enroll_student(i)
