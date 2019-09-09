"""These functions help organise enrolment, in particular for freshmen and ISIM.

Group splitting is going to be used in two ways: One is creating separate groups
for ISIM and CS students. This aims to solve the problem of ISIM students being
handicapped in the enrolment by having fewer ECTS credits and later opening
times.

The second is creating three bags of freshmen students ('tura1', 'tura2', and
'tura3'), splitting the most desired course groups into 3, and attaching
different opening times to these groups. It lets off-load the system a bit in
the most heated moment.

Usage in new semester scenario:
  1. Import schedule from the scheduler.
  2. Create groups for ISIM using split_out_isim function.
  3. Select freshmen groups for splitting and split them using split_in_three.
  4. Set semester enrolment opening time on the admin page.
  5. Click «Refresh opening times» on the admin page.
  6. Run adjust_split_in_three_opening_times.
  7. If you want to change general enrollment time or someone's personal bonus,
     remember to do 5. and 6.
  8. At some point you may want to merge groups using merge_groups function. To
     merge three freshmen virtual groups set merge_queues argument to False. To
     merge regular group with ISIM virtual group set it to True.
"""
from datetime import timedelta
from typing import List

from django.contrib.auth.models import Group as AuthGroup
from django.db import transaction

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record, RecordStatus, T0Times, GroupOpeningTimes
from apps.enrollment.records.models.opening_times import ProgramGroupRestrictions
from apps.enrollment.timetable.models import HiddenGroups
from apps.schedulersync.models import TermSyncData
from apps.users.models import Student, Program


@transaction.atomic
def merge_groups(group: Group, merge_queues: bool = False):
    """Merges the provided course group with its sister groups.

    Sister groups are the ones who correspond to the same proposal in scheduler.
    The limit of the resulting group will be a sum of the limits of the mergees.
    Every student enrolled into one of the merged groups will be enrolled into
    the resulting group, but the new group's queue is going to be empty unless
    'merge_queues' is True. The merged groups are going to be deleted.

    The function assumes that all the data other than the limit are the same for
    the merged groups.

    The function is transactional.
    """

    term_sync_data_objects: List[TermSyncData] = []
    for term in group.term.all():
        term_sync_data_objects.extend(term.termsyncdata_set.all())
    scheduler_ids = [tsc.scheduler_id for tsc in term_sync_data_objects]
    mergees = [
        t.group for t in Term.objects.filter(
            termsyncdata__scheduler_id__in=scheduler_ids,
            group__course__semester=group.course.semester_id).prefetch_related('classrooms')
    ]
    mergees = list(mergees)
    print("Merging groups:", mergees)
    if mergees is None:
        return
    res = Group.copy(mergees[0])
    res.limit = sum([m.limit for m in mergees])
    res.extra = ''
    res.save()

    Record.objects.filter(group__in=mergees, status=RecordStatus.ENROLLED).update(group=res)
    if merge_queues:
        Record.objects.filter(group__in=mergees, status=RecordStatus.QUEUED).update(group=res)
    for m in mergees:
        # This will also remove the corresponding Term, TermSyncData,
        # schedule.Event, schedule.Terms, and timetable.HiddenGroups.
        m.delete()


@transaction.atomic
def split_out_isim(group: Group, limit_isim=0) -> Group:
    """Separates out an ISIM virtual group out of the provided course group.

    The ProgramRestrictions are added so that ISIM students are not able to
    enrol into the regular group and the regular students cannot join the ISIM
    group.
    """
    isim_group = Group.copy(group)
    isim_group.limit = limit_isim
    group.limit -= limit_isim
    isim_group.extra = 'ISIM'
    isim_group.save()
    group.save()
    prog_isim = Program.objects.get(name="ISIM, dzienne I stopnia")
    progs_others = Program.objects.all().exclude(id=prog_isim.id)
    program_restrictions = [ProgramGroupRestrictions(group=group, program=prog_isim)]
    for p in progs_others:
        program_restrictions.append(ProgramGroupRestrictions(group=isim_group, program=p))

    ProgramGroupRestrictions.objects.bulk_create(program_restrictions)
    isim_role = AuthGroup.objects.get(name='stud_isim')
    notisim_role = AuthGroup.objects.get(name='stud_notisim')
    # Hide groups from students to tidy their prototypes.
    HiddenGroups.objects.bulk_create([
        HiddenGroups(group=group, role=isim_role),
        HiddenGroups(group=isim_group, role=notisim_role),
    ])


@transaction.atomic
def split_in_three(group: Group):
    """Splits the provided course group into three groups for freshmen.

    The resulting groups' extra field will be labelled 'tura1', 'tura2', 'tura3'
    to match freshmen role groups. The limits are going to be distributed
    evenly. The new groups will be hidden from the prototype of students, that
    should not see them.

    This function is transactional. It will fail, if the provided group already
    has an 'extra' tag.
    """
    assert len(group.extra) == 0
    group1 = group
    group2 = Group.copy(group)
    group3 = Group.copy(group)
    # Assign the groups to the freshmen.
    group1.extra = 'tura1'
    group2.extra = 'tura2'
    group3.extra = 'tura3'
    # Distribute the limit.
    lim = group.limit
    newlim = lim // 3
    group1.limit = newlim
    group2.limit = newlim
    group3.limit = newlim
    if lim % 3 == 1:
        group2.limit += 1
    elif lim % 3 == 2:
        group2.limit += 1
        group1.limit += 1
    group1.save()
    group2.save()
    group3.save()
    tura1 = AuthGroup.objects.get(name='tura1')
    tura2 = AuthGroup.objects.get(name='tura2')
    tura3 = AuthGroup.objects.get(name='tura3')
    # Hide the groups from other students than their own.
    HiddenGroups.objects.bulk_create([
        HiddenGroups(group=group1, role=tura2),
        HiddenGroups(group=group1, role=tura3),
        HiddenGroups(group=group2, role=tura1),
        HiddenGroups(group=group2, role=tura3),
        HiddenGroups(group=group3, role=tura1),
        HiddenGroups(group=group3, role=tura2),
    ])


@transaction.atomic
def adjust_split_in_three_opening_times():
    """Computes the opening times for freshmen and their virtual groups.

    The times are computed relative to the student's T0. If he is in 'tura1'
    group, his opening time for 'tura1'-labelled course group is going to be
    8:30 hours before his T0. For 'tura2' and 'tura3' this is going to be 8:00
    and 7:30 respectively. This way, if enrollment starts at 00:00 as it usually
    happens, they will be able to enroll into their respective groups at 13:30,
    14:00 and 14:30 on the previous day.

    The function is transactional. It will fail if any of the students in
    question already has an opening time bonus in a group (usually earned by
    voting for the course).
    """

    def bonus(label: str) -> timedelta:
        if label == 'tura1':
            return timedelta(hours=8, minutes=30)
        if label == 'tura2':
            return timedelta(hours=8)
        if label == 'tura3':
            return timedelta(hours=7, minutes=30)

    semester = Semester.objects.get_next()
    opening_times: List[GroupOpeningTimes] = []
    for label in 'tura1', 'tura2', 'tura3':
        groups = Group.objects.filter(course__semester=semester, extra=label)

        # Find all corresponding lecture groups.
        courses = CourseInstance.objects.filter(groups__in=groups).distinct()
        lecture_groups = []
        for c in courses:
            lecture_groups.extend(Group.get_lecture_groups(c))

        role = AuthGroup.objects.get(name=label)
        students = Student.objects.filter(status=0, user__groups=role)
        t0times = T0Times.objects.filter(semester=semester, student__user__groups=role)
        t0times = {t0.student_id: t0.time for t0 in t0times}

        for student in students:
            for group in groups:
                opening_times.append(
                    GroupOpeningTimes(
                        student=student, group=group, time=t0times[student.pk] - bonus(label)))
            for group in lecture_groups:
                opening_times.append(
                    GroupOpeningTimes(
                        student=student, group=group, time=t0times[student.pk] - bonus(label)))

    GroupOpeningTimes.objects.bulk_create(opening_times)
