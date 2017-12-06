# -*- coding: utf-8 -*-
"""
    Forms used to apps.grade courses
"""
from django                   import forms
from django.utils.safestring  import SafeText
from django.core.exceptions   import ValidationError, \
                                     ObjectDoesNotExist
from django.core.validators   import MaxLengthValidator

from apps.grade.poll.models import SingleChoiceQuestionOrdering, \
                                     Section, OpenQuestionAnswer, \
                                     SingleChoiceQuestionAnswer, \
                                     MultipleChoiceQuestionAnswer


from apps.enrollment.courses.models      import Semester

class TicketsForm( forms.Form ):
    ticketsfield = forms.CharField( widget = forms.widgets.Textarea(
                                                    attrs = {'cols' : 80,
                                                             'rows' : 20 }),
                                 label     = "Podaj wygenerowane bilety",
                                 help_text = "Wklej tutaj pobrane wcześniej bilety.",
                                 required  = False )
    ticketsfile = forms.FileField( widget=forms.HiddenInput,
                                   label    = "Lub wybierz plik z biletami:",
                                   required = False )


class MaxAnswersValidator(MaxLengthValidator):
    compare = lambda self, a, b: (b!=0) and (a > b)


class PollForm( forms.Form ):
    class myObject:
        pass

    #- wydzielic do forma Section
    def as_edit(self):
        from django.template import loader
        return loader.render_to_string('grade/poll/section_as_edit.html', {"sections": self.sections})

    def as_divs(self, errors = None):
        from django.template import loader
        return loader.render_to_string('grade/poll/poll_show.html', {"errors": errors, "sections": self.sections})

    def setFields( self, poll = None, st = None, section_id = None, post_data = None ):
        self.instance = poll
        if st:
            self.finished = st.finished
        else:
            self.finished = True

        if poll:
            ppk = poll.pk
        else:
            ppk = 0

        self.sections = []

        if section_id:
            sections_set = []
            sections_set.append( Section.objects.get(pk = section_id))
        elif poll:
            sections_set = poll.all_sections()
        else:
            section_set = {}

        for section in sections_set:
            title     = 'poll-%d_section-%d' % ( ppk, section.pk )
            questions = section.all_questions()
            fields    = []
            poll_section             = self.myObject()
            poll_section.title       = section.title
            poll_section.description = section.description
            poll_section.questions   = []
            poll_section.leading     = False
            if str( type( questions[ 0 ])) == \
                "<class 'apps.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                questionOrdering  = SingleChoiceQuestionOrdering.objects.select_related().get(
                        sections = section,
                        question = questions[ 0 ])
                if questionOrdering.is_leading:
                    title   += '_question-%d-leading' % questions[ 0 ].pk
                    if post_data:
                        answer = post_data.get( title, None )
                    else:
                        try:
                            answer = SingleChoiceQuestionAnswer.objects.select_related().get(
                                        saved_ticket = st,
                                        section      = section,
                                        question     = questions[ 0 ] ).option.pk
                        except ObjectDoesNotExist:
                            answer = None

                    choices = []
                    for option in questions[ 0 ].options.all().order_by('pk'):
                        choices.append(( option.pk, str( option.content )))

                    field = forms.ChoiceField(
                                choices  = choices,
                                label    = str( questions[ 0 ].content ),
                                required = False,
                                widget   = forms.widgets.RadioSelect(),
                                initial  = answer )

                    field.is_leading     = True
                    poll_section.leading = True
                    section
                    field.hide_on    = [x.pk for x in questionOrdering.hide_on.all()]
                    field.title      = title
                    field.description = questions[ 0 ].description
                    if not field.description: field.description = ""
                    field.is_scale    = questions[ 0 ].is_scale
                    field.type       = 'single'
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    poll_section.questions.append( field )

                    if self.finished: field.disabled = True
                    self.fields[ str( title ) ] = field
                    questions = questions[ 1: ]

            for question in questions:
                title = 'poll-%d_section-%d_question-%d' % ( ppk, section.pk, question.pk )
                if str( type( question )) == \
                    "<class 'apps.grade.poll.models.single_choice_question.SingleChoiceQuestion'>":
                    title += '-single'

                    if question.is_scale:
                        title += '-scale'

                    if post_data:
                        answer = post_data.get( title, None )
                    else:
                        try:
                            answer = SingleChoiceQuestionAnswer.objects.get(
                                        saved_ticket = st,
                                        section      = section,
                                        question     = question ).option.pk
                        except ObjectDoesNotExist:
                            answer = None

                    choices = []
                    for option in question.options.all().order_by('pk'):
                        choices.append(( option.pk, str( option.content )))

                    field = forms.ChoiceField( choices  = choices,
                                               label    = str( question.content ),
                                               required = False,
                                               widget   = forms.widgets.RadioSelect(),
                                               initial  = answer )
                    field.type = 'single'
                    if title.endswith( 'scale' ): field.scale = True
                    field.description      = question.description
                    if not field.description: field.description = ""
                    if question.is_scale: field.is_scale  = True
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    field.title        = title
                    if self.finished: field.disabled = True
                    poll_section.questions.append( field )
                    self.fields[ str( title ) ] = field
                elif str( type( question )) == \
                    "<class 'apps.grade.poll.models.multiple_choice_question.MultipleChoiceQuestion'>":
                    title += '-multi'

                    if post_data:
                        answer    = list(map( int, post_data.getlist( title )))
                        if -1 in answer:
                            other_ans = post_data.get( title + '-other', None )
                        else:
                            other_ans = None
                    else:
                        try:
                            answer   = MultipleChoiceQuestionAnswer.objects.get(
                                          saved_ticket = st,
                                          section      = section,
                                          question     = question)
                            other_ans = answer.other
                            answer    =  [x.pk for x in answer.options.all()]
                        except ObjectDoesNotExist:
                            answer    = None
                            other_ans = None
                    choices = []
                    for option in question.options.all().order_by('pk'):
                        choices.append(( option.pk, str( option.content )))
                    other_field = None
                    if question.has_other:
                        choices.append(( -1, str( 'Inne' )))
                        other_field = forms.CharField(
                                        label    = '',
                                        initial  = other_ans,
                                        required = False )
                        other_field.title = title + '-other'
                        other_field.type  = 'other'
                        if self.finished: other_field.widget.attrs[ 'disabled' ] = True
                        if other_ans and -1 not in answer: answer.append( -1 )
                    if answer:
                        choosed = len( answer )
                    else:
                        choosed = 0
                    field = forms.MultipleChoiceField(
                                choices        = choices,
                                label          = str( question.content ),
                                required       = False,
                                widget         = forms.widgets.CheckboxSelectMultiple(),
                                initial        = answer,
                                validators     = [ MaxAnswersValidator( question.choice_limit )],
                                error_messages = { "max_length": "Można wybrać maksymalnie %d odpowiedzi (wybrano %d)" % (question.choice_limit, choosed ) })
                    field.choice_limit     = question.choice_limit
                    field.has_other        = question.has_other
                    field.description      = question.description
                    if not field.description: field.description = ""
                    field.type             = 'multi'
                    field.title = title
                    if self.finished: field.disabled = True
                    poll_section.questions.append( field )
                    self.fields[ str( title ) ] = field
                    if question.has_other:
                        field.other = other_field
                        self.fields[ str(other_field.title) ] = other_field
                elif str( type( question )) == \
                    "<class 'apps.grade.poll.models.open_question.OpenQuestion'>":
                    title += '-open'

                    if post_data:
                        answer = post_data.get( title, None )
                    else:
                        try:
                            answer = OpenQuestionAnswer.objects.get(
                                        saved_ticket = st,
                                        section      = section,
                                        question     = question ).content
                        except ObjectDoesNotExist:
                            answer = ""

                    field = forms.CharField(
                                widget = forms.widgets.Textarea(
                                                attrs = { 'cols'  : 80,
                                                          'rows'  : 20 }),
                                label  = str( question.content ),
                                required = False,
                                initial  = answer )
                    if self.finished: field.widget.attrs[ 'disabled' ] = True
                    field.type    =  'open'
                    field.title = title
                    field.description      = question.description
                    if not field.description: field.description = ""
                    if self.finished: field.disabled = True
                    poll_section.questions.append( field )
                    self.fields[ str( title ) ] = field

            if section.pk:
                poll_section.pk = section.pk

            self.sections.append(poll_section)
        if not self.finished:
            field = forms.BooleanField(
                            label     = 'Zakończ oceniać',
                            required  = False,
                            initial   = False,
                            help_text = 'Ankieta zakończona - Jeśli zaznaczysz to pole, utracisz mozliwość edycji tej ankiety.' )
            field.type  = 'finish'
            self.finish = field
            self.fields[ 'finish' ] = field


class FilterMenu( forms.Form ):

    sem = Semester.objects.all()

    li = []

    for s in  sem:
        li.append(s.year)

    li.sort()

    li = list(set(li))

    begin = []
    end = []

    for l in li:
        begin.append((l,l))
        end.append((l,l))

    semestr_date_begin  =   forms.ChoiceField( label = 'od', choices = begin )
    semestr_date_end    =   forms.ChoiceField( label = 'do', choices = begin )

    semestr_winter      =   forms.BooleanField( label = 'zimowy' )
    semestr_summer      =   forms.BooleanField( label = 'letni' )

    own_resource        =   forms.BooleanField( label = 'własne' )
    available_resource  =   forms.BooleanField( label = 'udostępnione' )

    lecture             =   forms.BooleanField( label = 'wykłady' )
    tutorial            =   forms.BooleanField( label = 'ćwiczenia' )
    lab                 =   forms.BooleanField( label = 'pracownie')

    order               =   forms.TypedChoiceField( widget=forms.RadioSelect, choices=((1,"wg nazwisk prowadzących"),(2,"wg nazw przedmiotów")))

    special             =   forms.BooleanField()
