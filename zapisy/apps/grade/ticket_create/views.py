# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from apps.grade.ticket_create.models.student_graded import StudentGraded
from apps.users.decorators import student_required, employee_required
from apps.users.models import BaseUser

from apps.enrollment.courses.models import Semester
from apps.grade.poll.models.poll import Poll
from apps.grade.ticket_create.utils import generate_keys_for_polls, generate_keys, group_polls_by_course, \
    secure_signer, unblind, get_valid_tickets, to_plaintext, connect_groups, secure_signer_without_save, secure_mark
from apps.grade.ticket_create.models import PublicKey
from django.contrib.auth import authenticate
from apps.grade.ticket_create.forms import ContactForm, PollCombineForm
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils.safestring import SafeUnicode


### KEYS generate:

@employee_required
def ajax_keys_generate( request ):
    generate_keys_for_polls()
    return HttpResponse("OK")

@employee_required
def ajax_keys_progress( request ):
    count = cache.get('generated-keys', 0)
    return HttpResponse(str(count))

@student_required
def ajax_get_rsa_keys_step1( request ):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student( request.user.student )
            groupped_polls = group_polls_by_course( students_polls )
            form = PollCombineForm( request.POST,
                                    polls = groupped_polls )
            if form.is_valid():
                connected_groups = connect_groups( groupped_polls, form )
                tickets = map( lambda gs: generate_keys( gs ),
                                      connected_groups )
                message = json.dumps(tickets)
    return HttpResponse(message)

@student_required
def ajax_get_rsa_keys_step2( request ):
    message = "No XHR"
    if request.is_ajax():
        if request.method == 'POST':
            students_polls = Poll.get_all_polls_for_student( request.user.student )
            groupped_polls = group_polls_by_course( students_polls )
            form = PollCombineForm( request.POST,
                                    polls = groupped_polls )
            if form.is_valid():
                ts               = json.loads(request.POST.get('ts'))
                connected_groups = connect_groups( groupped_polls, form )
                groups           = reduce(list.__add__, connected_groups )
                tickets          = zip( groups, ts)
                signed = map( lambda ( g, t):
                            (g, long(t), secure_signer_without_save( request.user, g, long(t) )),
                             tickets )
                unblinds = map ( lambda ( g, t, st ):
                                (unicode(t), unblind( g, st ) ),
                             signed )
                message = json.dumps(unblinds)
    return HttpResponse(message)

@student_required
def connections_choice( request ):

    grade = Semester.objects.filter(is_grade_active=True).count() > 0
    students_polls = Poll.get_all_polls_for_student( request.user.student )
    if students_polls:
        semester = students_polls[0].semester
    else:
        semester = None
    groupped_polls = group_polls_by_course( students_polls )
    polls_lists, general_polls = Poll.get_polls_list( request.user.student ) #
    connected = any(len(x) > 1 for x in groupped_polls)
    if grade:
        if request.method == "POST":
            form = PollCombineForm( request.POST,
                                    polls = groupped_polls )
            if form.is_valid():
                unblindst = json.loads(request.POST.get('unblindst', ''))
                unblindt  = json.loads(request.POST.get('unblindt', ''))
                ts        = json.loads(request.POST.get('ts', ''))
                connected_groups = connect_groups( groupped_polls, form)
                if connected_groups:
                    groups           = reduce(list.__add__, connected_groups )
                else:
                    groups = []
                prepared_tickets = zip( groups, unblindt, unblindst )
                #### final mark:
                for g, t, unblind in prepared_tickets:
                    secure_mark(request.user, g, t )
                errors, tickets_to_serve = get_valid_tickets( prepared_tickets )
                if errors:
                    message = u'Nie udało się pobrać następujących biletów:\n<ul>'
                    for poll, reason in errors:
                        message += u"<li>Ankieta: " + unicode( poll )
                        message += u"<br>Powód: "
                        message += unicode( reason )
                        message += u"</li>"
                    message += u"</ul>"
                    messages.error( request, SafeUnicode( message ))
                data = { 'tickets' : to_plaintext( tickets_to_serve ),
                         'grade' : grade }

                if tickets_to_serve:
                    StudentGraded.objects.get_or_create(student=request.user.student,
                                                      semester=semester)

                return render(request, "grade/ticket_create/tickets_save.html", data)

        else:
           pass
#             form = PollCombineForm( polls = groupped_polls )

        data = { 'polls':polls_lists, 'grade' : grade, 'general_polls': general_polls}
        return render(request, 'grade/ticket_create/connection_choice.html', data)
    else:
        messages.error( request, "Ocena zajęć jest w tej chwili zamknięta; nie można pobrać biletów" )
        return render(request, 'grade/ticket_create/connection_choice.html', { 'grade': grade })


@csrf_exempt
def client_connection( request ):
    if request.method == 'POST':

        form = ContactForm(request.POST)

        if form.is_valid():
            idUser = form.cleaned_data['idUser']
            passwordUser = form.cleaned_data['passwordUser']
            groupNumber = form.cleaned_data['groupNumber']
            groupKey = long(form.cleaned_data['groupKey'])

            user = authenticate(username=idUser, password=passwordUser)

            if user is None:
                return HttpResponse(u"nie ma takiego użytkownika")
            if BaseUser.is_student(user):
                return HttpResponse(u"użytkownik nie jest studentem")


            if groupNumber == u"*":
                st=u""
                students_polls = Poll.get_all_polls_for_student( user.student )

                if students_polls:
                    semester = students_polls[0].semester
                    StudentGraded.objects.get_or_create(student=user.student,
                                                      semester=semester)
                groupped_polls = group_polls_by_course( students_polls )
                for polls in groupped_polls:

                    if len( polls ) == 1:

                        st += unicode( polls[0].pk ) + u'***'
                        st += u'[' + unicode( polls[0].title ) + u']%%%'

                        if polls[0].group:
                            st += unicode( polls[0].group.course.name ) + u'%%%'
                            st += unicode( polls[0].group.get_type_display()) + u': %%%'
                            st += unicode( polls[0].group.get_teacher_full_name()) + u'%%%'

                        st +=unicode( '***' )

                        st += unicode( PublicKey.objects.get( poll = polls[0].pk ).public_key ) + u'???'

                    else:
                        for poll in polls:
                            st += unicode( poll.pk ) + u'***'
                            if not poll.group:
                                st += u'Ankiety ogólne: %%%   [' + poll.title + '] '
                            else:
                                st += u'Przedmiot: ' + polls[ 0 ].group.course.name + u'%%%    [' + poll.title + u'] ' + \
                                         poll.group.get_type_display() + u': ' + \
                                         poll.group.get_teacher_full_name() + u'***'
                                st += unicode( PublicKey.objects.get( poll = poll.pk ).public_key ) + '&&&'
                        st += u'???'

                return HttpResponse( st )


            students_polls = Poll.get_all_polls_for_student( user.student )

            st = ""

            for students_poll in students_polls:
                if int(students_poll.pk) == int(groupNumber):

                    st = secure_signer_without_save( user, students_poll, groupKey)
                    secure_signer( user, students_poll, groupKey )
                    p = students_poll
                    break
            if st == "":
                st = u"Nie jesteś zapisany do tej ankiety"


            try:
                a=long(st[0][0])
            except ValueError, err:
                return HttpResponse(st)
            if   st == u"Nie jesteś zapisany do tej ankiety":
                return HttpResponse(st)
            elif st == u"Bilet już pobrano":
                return HttpResponse(st)
            else:
                return HttpResponse( to_plaintext( [(p,u'***',u'%%%')] ) + u'???' + unicode(a) )


@csrf_exempt
def keys_list( request ):
    l = PublicKey.objects.all()#.order_by('poll__group__course__name')
    return render(request, 'grade/ticket_create/keys_list.html', {'list': l,})

@csrf_exempt
def keys_generate( request ):
    data = {}
    data['keys_to_create'] = Poll.count_polls_without_keys()
    return render(request, 'grade/ticket_create/keys_generate.html', data)
