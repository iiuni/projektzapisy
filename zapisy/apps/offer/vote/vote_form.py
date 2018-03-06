
"""
    Form for vote
"""

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.db import connection
from django.db.models import Sum
from django.utils.safestring  import SafeText
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.vote.models import SystemState
from apps.offer.vote.models import SingleVote
from django.core.urlresolvers import reverse

from django.conf import settings

class VoteFormset(object):
    """
        Class

        które do poprawki? te które mają

    """

    def __init__(self, post, *args, **kwargs):
        from django.forms.models import modelformset_factory
        tag             = kwargs.pop('tag',        None)
        student         = kwargs.pop('student',    None)
        state           = kwargs.pop('state',    None)
        semester_id     = None
        self.correction = kwargs.pop('correction', False)

        query = {}
        query['status'] = CourseEntity.STATUS_TO_VOTE
        query['deleted'] = False

        if tag == 'winter':
            query['semester'] = 'z'
            semester_id = state.semester_winter_id
        elif tag == 'summer':
            query['semester'] = 'l'
            semester_id = state.semester_summer_id
        else:
            tag = 'unknown'
            query['semester'] = 'u'
        proposals  = CourseEntity.simple.filter(**query)
        votes = SingleVote.get_votes_for_proposal(student, proposals)
        if self.correction:
            votes = votes.extra(where=['(SELECT COUNT(*) FROM courses_course cc WHERE cc.entity_id = vote_singlevote.entity_id AND cc.semester_id = '+ str(semester_id) +') > 0'])
        counter = votes.exclude(entity__type__free_in_vote=True).aggregate(Sum('value'))

#        if self.correction:
#            votes = votes.filter(course__isnull=False)


        fields = ('correction',) if self.correction else ('value',)


        SingleVoteFormset = modelformset_factory( SingleVote,
                                                  fields = fields,
                                                  extra  = 0 )

        self.formset = SingleVoteFormset(post,
                                         queryset = votes,
                                         prefix   = tag )
        self.errors  = []

    def points(self):
        counter = 0

        field = 'correction' if self.correction else 'value'

        for form in self.formset:
            if not form.instance.entity.type.free_in_vote:
                counter += form.cleaned_data[field]

        return counter

    def is_valid(self):

        if self.formset.is_valid():
            sum_points = 0
            if self.correction:
                for form in self.formset:
                    sum_points += form.cleaned_data['correction']
                    if form.instance.value > form.cleaned_data['correction']:
                        self.errors.append( 'Nie można zmniejszyć głosu!' )
                        return False

            return True

        return False


    def save(self):



        if not self.correction:
            instances = self.formset.save(commit=False)
            for instance in instances:
                instance.correction = instance.value
                instance.save()

            return instances

        else:
            return self.formset.save()


class VoteFormsets():

    def __init__(self, post=None, student=None, state=None, *args, **kwargs):
        self.summer = None
        self.winter = None
        self.unknown = None
        if state.is_correction_active():
            self.points_limit = 0

            if state.is_summer_correction_active():
                self.points_limit += SingleVote.limit_in_summer_correction(student, state)
                self.summer  = VoteFormset(post,
                                           student    = student,
                                           tag        = 'summer',
                                           state      = state,
                                           correction = True)

            if state.is_winter_correction_active():
                self.points_limit += SingleVote.limit_in_winter_correction(student, state)
                self.winter  = VoteFormset(post,
                                       student    = student,
                                       tag        = 'winter',
                                      state      = state,
                                       correction = True)

            self.errors = []

        else:
            self.points_limit = state.max_points

            self.summer  = VoteFormset(post,
                                       student    = student,
                                       tag        = 'summer',
                                       state      = state)
            self.winter  = VoteFormset(post,
                                       student    = student,
                                       tag        = 'winter',
                                       state      = state)
            self.unknown = VoteFormset(post,
                                       student    = student,
                                       state      = state)
            self.errors = []


    def points(self):
        points = 0
        if self.summer:
            points += self.summer.points()
        if self.winter:
            points += self.winter.points()
        if self.unknown:
            points += self.unknown.points()

        return points

    def is_valid(self):
        is_valid = (not self.summer or self.summer.is_valid()) and\
                   (not self.winter or self.winter.is_valid()) and\
                   (not self.unknown or self.unknown.is_valid())

        if self.summer:
            self.errors = self.errors + self.summer.errors
        if self.winter:
            self.errors = self.errors + self.winter.errors
        if self.unknown:
            self.errors = self.errors + self.unknown.errors

        if not is_valid:
            return False


        points = self.points()
        if  points > self.points_limit:
            self.errors.append('Limit ' + str(self.points_limit) +' punktów przekroczony o ' + \
                               str((points - self.points_limit)) )
            return False


        return True


    def save(self):
        if self.summer:
            self.summer.save()
        if self.winter:
            self.winter.save()
        if self.unknown:
            self.unknown.save()
