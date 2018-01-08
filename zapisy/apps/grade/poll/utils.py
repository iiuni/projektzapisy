# -*- coding: utf-8 -*-
import re
import StringIO
import csv
from Crypto.PublicKey                 import RSA
from apps.grade.poll.models          import Poll, Section, SectionOrdering, \
                                              OpenQuestion, SingleChoiceQuestion, \
                                              OpenQuestionOrdering, Option, \
                                              SingleChoiceQuestionOrdering, \
                                              MultipleChoiceQuestion, \
                                              MultipleChoiceQuestionOrdering, \
                                              SavedTicket, \
                                              SingleChoiceQuestionAnswer, \
                                              MultipleChoiceQuestionAnswer, \
                                              OpenQuestionAnswer, Option, Template, \
                                              TemplateSections, Origin
from apps.grade.ticket_create.utils import poll_cmp, \
                                             flatten
from apps.enrollment.records.models        import Group
from apps.grade.poll.exceptions             import NoTitleException, NoPollException, \
                                                    NoSectionException

from apps.enrollment.courses.models import Semester, Group, Course, GROUP_TYPE_CHOICES, CourseEntity
from apps.users.models               import Program

from django.core.paginator             import Paginator, InvalidPage, EmptyPage
from django.utils.safestring           import SafeUnicode, mark_safe
from django.db.models import Q

def check_signature( ticket, signed_ticket, public_key ):
    pk = RSA.importKey( public_key.public_key )
    return pk.verify( ticket, (signed_ticket,) )

def group_polls_and_tickets_by_course( poll_and_ticket_list ):
    if not poll_and_ticket_list: return []

    poll_and_ticket_list.sort( lambda (p1, t1, st1), (p2, t2, st2): poll_cmp( p1, p2 ))

    res       = []
    act_polls = []
    act_group = poll_and_ticket_list[ 0 ][ 0 ].group

    for ( poll, ticket, signed_ticket ) in poll_and_ticket_list:
        if   not act_group:
            if   poll.group == act_group:
                act_polls.append(( poll.pk, ticket, signed_ticket ))
            else:
                res.append(( u'Ankiety ogólne', act_polls ))
                act_group = poll.group
                act_polls = [( poll.pk, ticket, signed_ticket )]
        else:
            if   poll.group.course == act_group.course:
                act_polls.append(( poll.pk, ticket, signed_ticket ))
            else:
                res.append(( unicode( act_group.course.name ), act_polls ))
                act_group = poll.group
                act_polls = [( poll.pk, ticket, signed_ticket )]

    if act_group:
        res.append(( unicode( act_group.course.name ), act_polls ))
    else:
        res.append(( u'Ankiety ogólne', act_polls ))

    return res

def create_slug( name ):
    """
        Creates slug
    """
    if name == u"Ankiety ogólne": return "common"

    slug = name.lower()
    slug = re.sub(u'ą', "a", slug)
    slug = re.sub(u'ę', "e", slug)
    slug = re.sub(u'ś', "s", slug)
    slug = re.sub(u'ć', "c", slug)
    slug = re.sub(u'ż', "z", slug)
    slug = re.sub(u'ź', "z", slug)
    slug = re.sub(u'ł', "l", slug)
    slug = re.sub(u'ó', "o", slug)
    slug = re.sub(u'ć', "c", slug)
    slug = re.sub(u'ń', "n", slug)
    slug = re.sub("\W", "-", slug)
    slug = re.sub("-+", "-", slug)
    slug = re.sub("^-", "", slug)
    slug = re.sub("-$", "", slug)
    return slug

def get_polls_for_course(( ( sub, slug ), get), groupped_polls ):
    if get:
        return ( sub, slug ), u'jest'
    else:
        return ( sub, slug ), []

def prepare_data( request, slug ):
    data = { 'errors'   : [],
             'polls'    : [],
             'finished' : [] }

    for id, error in request.session.get( 'errors', default = [] ):
        try:
            p = Poll.objects.get( pk = id )
            data[ 'errors' ].append( "%s: %s" % ( unicode( p ), error ))
        except:
            data[ 'errors' ].append( error )

    try:
        del request.session[ 'errors' ]
    except KeyError:
        pass

    polls = request.session.get( "polls", default = [] )
    dict  = {}
    if polls:
        polls_id = reduce(lambda x, y: x + y, map( lambda ((x, s), l):
                                map( lambda (id, t, st):
                                        id,
                                    l), polls))
        for poll in Poll.objects.filter(pk__in=polls_id).select_related('group', 'group__course', 'group__teacher', 'group__teacher__user'):
            dict[poll.pk] = poll

        data[ 'polls' ]    = map( lambda ((x, s), l):
                                ((x, s),
                                slug==s,
                                map( lambda (id, t, st):
                                        (id, t, st, dict[id].to_url_title( True )),
                                    l)),
                            polls)
    else:
        data[ 'polls' ] = []
    finished    = request.session.get( "finished", default = [] )
    if finished:
        finished_id = reduce(lambda x, y: x + y, map( lambda ((x, s), l):
                                map( lambda (id, t, st):
                                        id,
                                    l), finished))
        for poll in Poll.objects.filter(pk__in=finished_id).select_related('group', 'group__course', 'group__teacher', 'group__teacher__user'):
            dict[poll.pk] = poll

        data[ 'finished' ] = map( lambda ((x, s), l):
                                ((x, s),
                                slug==s,
                                map( lambda (id, t, st):
                                        (id, t, st, dict[id].to_url_title( True )),
                                    l)),
                            finished)
    else:
        data[ 'finished' ] = []

    data[ 'finished_polls' ] = len(request.session.get( "finished", default = [] ))
    data[ 'all_polls']  = reduce(lambda x, y: x + y,
                                   map( lambda (p, l): len(l),
                                    request.session.get( "polls", default = [] )), data[ 'finished_polls' ])
    return data

def get_next( poll_list, finished_list, poll_id ):
    ret = False
    for (p_id, t, st, s), slug in poll_list:
        if ret: return p_id, t, s, slug
        ret = p_id == poll_id

    ret = False
    for (p_id, t, st, s), slug in finished_list:
        if ret: return p_id, t, s, slug
        ret = p_id == poll_id

    return None

def get_prev( poll_list, finished_list, poll_id ):
    poll_list.reverse()
    finished_list.reverse()

    prev = get_next( poll_list, finished_list, poll_id )

    poll_list.reverse()
    finished_list.reverse()

    return prev

def get_ticket_and_signed_ticket_from_session( session, slug, poll_id ):
    polls    = session.get( 'polls', default = [])
    finished = session.get( 'finished', default = [])

    polls    = flatten( map(lambda ((n,s), lt): lt, filter( lambda ((name, s), lt): s == slug, polls)))
    finished = flatten( map(lambda ((n,s), lt): lt, filter( lambda ((name, s), lt): s == slug, finished)))

    data = polls + finished
    data = map( lambda (id, t, st): (t, st), filter( lambda (id, t, st): id == int( poll_id ), data ))

    try:
        return data[0]
    except IndexError:
        return None, None

def getGroups(request, template):


    if template['course'] == -1:
        return {}

    if template['group']:
        return template['group']

    kwargs = {}

    if template['semester']:
        kwargs['course__semester'] = template['semester']

    if template['course']:
        kwargs['course__entity'] = template['course']

    if template['type']:
        kwargs['type'] = template['type']

    if 'exam' in template and template['exam']:
        kwargs['course__entity__exam'] = True

    return Group.objects.filter(**kwargs)

def poll_cmp_courses( p1, p2 ):
    if p1.group:
        if p2.group:
            return cmp( p1.group.course.name, p2.group.course.name )
        else:
            return 1
    else:
        return -1

def poll_cmp_teachers( p1, p2 ):
    if p1.group:
        if p2.group:
            return cmp( p1.group.get_teacher_full_name(), p2.group.get_teacher_full_name() )
        else:
            return 1
    else:
        return -1

def group_polls_by_course( polls ):
    polls.sort( poll_cmp_courses )

    groupped = []
    if polls:
        try:
            act_sub = polls[ 0 ].group.course.name
        except:
            act_sub = u"Ankiety ogólne"
        act = [ polls[ 0 ]]
        polls = polls[ 1: ]

        for poll in polls:
            try:
                sub = poll.group.course.name
            except:
                sub = u"Ankiety ogólne"

            if sub == act_sub:
                act.append( poll )
            else:
                groupped.append(( act_sub, act ))
                act     = [ poll ]
                act_sub = sub
        if act: groupped.append(( act_sub, act ))
    return groupped


def group_polls_by_teacher( polls ):
    polls.sort( poll_cmp_teachers )

    groupped = []
    if polls:
        try:
            act_sub = polls[ 0 ].group.get_teacher_full_name()
        except:
            act_sub = u"Ankiety ogólne"
        act = [ polls[ 0 ]]
        polls = polls[ 1: ]

        for poll in polls:
            try:
                sub = poll.group.get_teacher_full_name()
            except:
                sub = u"Ankiety ogólne"

            if sub == act_sub:
                act.append( poll )
            else:
                groupped.append(( act_sub, act ))
                act     = [ poll ]
                act_sub = sub
        if act: groupped.append(( act_sub, act ))
    return groupped

def declination_poll(num, nominative = False):
    if num == 1:
        if nominative:
            return u'ankieta'
        else:
            return u'ankietę'
    if ((num % 10) in [2,3,4] and (num < 10 or num > 20)):
        return u'ankiety'
    return u'ankiet'


def declination_section(num, nominative = False):
    if num == 1:
        if nominative:
            return u'sekcja'
        else:
            return u'sekcję'
    if ((num % 10) in [2,3,4] and (num < 10 or num > 20)):
        return u'sekcje'
    return u'sekcji'

def declination_template(num):
    if num == 1:
        return u'szablon'
    if num in [2,3,4]:
        return u'szablony'
    return 'szablonów'

####  HELPER FOR UNICODE + CSV -- Python's CSV does not support unicode

class UnicodeWriter(object):

    def __init__(self, f, dialect=csv.excel_tab, encoding="utf-16", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoding = encoding

    def writerow(self, row):
        # Modified from original: now using unicode(s) to deal with e.g. ints
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = data.encode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#### CSV file preparation

def generate_csv_title(poll):
    res = poll.title
    try:
        res += u' ' + poll.group.course.name
        res += u' ' + poll.group.get_type_display()
        res += u' ' + poll.group.get_teacher_full_name()
    except:
        res += u' ' + u'Ankieta ogólna'
    res += u' ' + unicode(poll.pk)
    res += u'.csv'
    return unicode(res)

def csv_prepare_header(sections):
    """
    csv_prepare_header prepares header for a specific poll - that is, it provides
    questions for the specific poll, prepared as reqired by the csv.writer
    """
    row = []
    for sec_questions in sections:
        row += sec_questions
    return row

def csv_prepare(handle, poll_sections, poll_data):
    """
    csv_prepare prepares the entire csv file - typically this is a file for
    a specific poll
    """
    #handle = StringIO.StringIO() #open(csv_title, 'wb')
    writer = UnicodeWriter(handle, delimiter=';', quotechar='"', quoting = csv.QUOTE_ALL)
    writer.writerow( csv_prepare_header(poll_sections) )
    for poll in poll_data:
        writer.writerow(poll)
    return handle

### POST DATA MANIPULATION

def get_objects( request, object ):
    """
    Get objects from post.

    @author mjablonski
    @param request
    @param object - type of returned objects, for example Poll, Section, Template

    @return set of objects type by param(object)
    """
    pks = request.POST.getlist('_selected_action')
    return object.objects.filter( pk__in=pks)

def delete_objects( request, object, object_list ):
    """
    Delete objects from post
    @author mjablonski
    @param request
    @param object - for example Poll, Section, Template
    @param object_list - object name in POST templates[], polls[]

    @return int - count of deleted objects
    """
    pks = request.POST.getlist(object_list)
    counter = 0
    for pk in pks:
        element = object.objects.get(pk=pk)
        element.deleted = True
        element.save()
        counter += 1

    return counter

def make_paginator( request, object=None, objects=None):
    """
    Prepare paginator to view.

    @author mjablonski
    @param request - request, for get
    @param object  - type of object to paginate for example Poll, Section
    """
    if object:
        objects = object.objects.filter(deleted=False)

    paginator = Paginator(objects, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        return paginator.page(page), paginator
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages), paginator

def course_list( courses ):
    course_list = []
    for course in courses:
        course_list.append( (course.pk , unicode(course.name)) )
    return course_list

def groups_list( groups ):
    group_list = []
    for group in groups:
        group_list.append( (group.pk, unicode(group.teacher)) )
    return group_list


#### TEMPLATES

def make_template_from_db( request, template):

    return dict(
        type           = None if template.group_type == '--' else template.group_type,
        sections       = template.sections.all(),
        studies_type   = template.studies_type,
        title          = template.title,
        description    = template.description,
        course         = template.course,
        semester       = Semester.objects.get(id=request.POST['semester']),
        groups_without = 'off',
        group          = None)


def make_template_variables( request ):
    """
        parse POST for template datas
        @author mjablonski

        @param request
        @return dictionary - templates option
    """
    var = {}

    if request.POST.get('title', '') == '':
        raise NoTitleException

    type         = int(request.POST.get('type', 0))
    if not type:
        type = None

    studies_type = int(request.POST.get('studies-type', -1))
    if studies_type > -1:
        studies_type = Program.objects.get(pk=studies_type)
    else:
        studies_type = None

    course      = int(request.POST.get('course', 0))
    if course > 0:
        course = CourseEntity.objects.get(pk=course)
    elif not course:
        course = None
    else:
        course = -1

    group        = int(request.POST.get('group', 0))
    if group > 0:
        group    = Group.objects.filter(pk = group)
    else:
        group    = None

    semester     = int(request.POST.get('semester', 0))
    if semester > 0:
        semester = Semester.objects.get(pk = semester)
    else:
        semester = Semester.get_current_semester()
    var['type']           = type
    var['studies_type']   = studies_type
    var['course']         = course
    var['title']          = request.POST.get('title', '')
    var['semester']       = semester
    var['description']    = request.POST.get('description', '')
    var['groups_without'] = request.POST.get('poll-only-without', 'off')
    var['group']           = group
    var['exam']           = request.POST.get('exam', False)
    return var

def prepare_template( request ):
    """Creates template from the request.
        @author mjablonski

        @param request
        @return Template

        Raises:
            Employee.DoesNotExist: If the user in the request is not an
                employee.
    """
    variables = make_template_variables( request )

    tmpl = Template()
    tmpl.title        = variables['title']
    tmpl.description  = variables['description']
    tmpl.studies_type = variables['studies_type']
    tmpl.exam         = variables['exam']
    tmpl.author       = request.user.employee

    if variables['course'] == -1:
        tmpl.no_course = True
        tmpl.course    = None
    else:
        tmpl.no_course = False
        tmpl.course    = variables['course']

    tmpl.group_type   = variables['type'] if variables['type'] else '--'

    tmpl.save()

    return tmpl


def prepare_sections_for_template( request, template):
    """
        Create sections in template from request
        @author mjablonski

        @param request
        @param Template template
    """
    sections_list = request.POST.getlist('sections[]')
    if not len(sections_list):
        raise NoSectionException

    for section in sections_list:
        sections          = TemplateSections()

        sections.template = template
        sections.section  = Section.objects.get(pk=section)
        sections.save()

def get_templates( request ):
    """
        Get templates from request
        @author mjablonski

        @param request
    """
    pks   = request.POST.getlist('templates[]')
    return Template.objects.filter(pk__in=pks)


def make_section_for_poll(request, poll, template={}):
    if 'sections' in template:
        sections = template['sections']
        if not sections:
            raise NoSectionException
        for section in sections:
            pollSection = SectionOrdering()
            pollSection.poll = poll
            pollSection.position = section.pk
            pollSection.section = section
            pollSection.save()

    else:
        sections = request.POST.getlist('sections[]')
        if not sections:
            raise NoSectionException

        for (i, section) in enumerate(sections):
            pollSection = SectionOrdering()
            pollSection.poll = poll
            pollSection.position = i
            pollSection.section = Section.objects.get(pk=int(section))
            pollSection.save()

def make_poll_from_template( request, template):
    """Returns a poll object based on the template.

    Raises:
        Employee.DoesNotExist: If the user is not an employee.
    """
    poll = Poll()
    poll.author       = request.user.employee
    poll.title        = template['title']
    poll.description  = template['description']
    poll.semester     = template['semester']
    poll.group        = template['iterate_group']
    poll.studies_type = template['studies_type']
    poll.save()

    return poll

def make_poll(request, template, group=None, origin=None):
    """Prepares a poll object for the group based on the template.

    Raises:
        Employee.DoesNotExist: If the user in the request is not an employee.
    """
    poll = Poll()
    poll.author       = request.user.employee
    poll.title        = template['title']
    poll.description  = template['description']
    poll.semester     = template['semester']
    poll.group        = group
    poll.studies_type = template['studies_type']
    poll.origin = origin
    poll.save()

    make_section_for_poll(request, poll, template)
    return poll

def make_polls_for_groups( request, groups, template ):
    polls = []

    origin = Origin()
    origin.save()
    for group in groups:
        if template['groups_without'] == 'on' and Poll.get_all_polls_for_group(group, template.semeter).count()>0:
            continue

        poll = make_poll(request, template, group, origin)
        polls.append(unicode(poll))

    if not len(polls):
        raise NoPollException
    return polls

def make_polls_for_all( request, template ):
    origin = Origin()
    origin.save()
    polls = []
    poll = make_poll(request, template, None, origin)

    polls.append(unicode(poll))

    if not len(polls):
        raise NoPollException
    return polls


def save_template_in_session( request, template ):
    request.session['studies_type'] =  template['studies_type']
    request.session['semester']     =  template['semester']
    request.session['group']        =  template['group']
    request.session['type']         =  template['type']
    request.session['course']      =  template['course']
    request.session['groups_without'] = template['groups_without']
    request.session['polls_len']    =  template['polls_len']

def pop_template_from_session( request ):
    template = {'studies_type': request.session.get('studies_type', None),
                'semester': request.session.get('semester', None), 'group': request.session.get('group', None),
                'type': unicode(request.session.get('type', 0)), 'course': request.session.get('course', None),
                'groups_without': request.session.get('groups_without', None),
                'polls_len': request.session.get('polls_len', None)}
    #clear session for future
    if 'studies_type' in request.session:
        del request.session['studies_type']
    if 'semester' in request.session:
        del request.session['semester']
    if 'group' in request.session:
        del request.session['group']
    if 'type' in request.session:
        del request.session['type']
    if 'course' in request.session:
        del request.session['course']
    if 'groups_without' in request.session:
        del request.session['groups_without']
    if 'polls_len' in request.session:
        del request.session['polls_len']
    return template

def make_message_from_polls( polls ):
    message  = "Utworzono ankiety!"
    message += ("<br>Liczba utworzonych ankiet: %d" % (len( polls )))
    message += "<ul>"
    for poll in polls:
        message += ("<li>%s</li>" % unicode(poll) )
    message += "</ul>"

    return message

def prepare_data_for_create_poll( request, group_id = 0 ):
    data = pop_template_from_session( request )

    if group_id > 0:
        group                = Group.objects.get(pk=group_id)
        data['group']        = group.pk
        data['type']         = group.type
        data['course_id']    = group.course.pk
        data['semester']     = group.course.semester.pk
        data['groups']       = Group.objects.filter(type=group.type, course=group.course).order_by('teacher')

    if data['semester']:
        data['courses'] = get_courses_for_user(request, data['semester'])
    else:
        semester_id      = Semester.get_current_semester()
        data['semester'] = semester_id
        data['courses'] = get_courses_for_user(request, semester_id)

    data['studies_types']    = Program.objects.all()
    data['semesters']        = Semester.objects.all()
    data['sections']         = Section.objects.filter(deleted=False)
    data['types']            = GROUP_TYPE_CHOICES

    return data

def prepare_data_for_create_template( request, group_id = 0 ):
    data = pop_template_from_session( request )

    if group_id > 0:
        group                = Group.objects.get(pk=group_id)
        data['group']        = group.pk
        data['type']         = group.type
        data['course_id']    = group.course.pk
        data['groups']       = Group.objects.filter(type=group.type, course=group.course).order_by('teacher')

    data['courses'] = CourseEntity.objects.all()

    data['studies_types']    = Program.objects.all()
    data['sections']         = Section.objects.filter(deleted=False)
    data['types']            = GROUP_TYPE_CHOICES

    return data

def get_courses_for_user(request, semester):
    """Returns courses owned by the user.

    Raises:
        Employee.DoesNotExist: If the user in the request is not 'staff' and
            not an employee.
    """
    if request.user.is_staff:
        return Course.objects.filter(semester=semester).order_by('entity__name')
    else:
        courses = Group.objects.filter(course__semester=semester, teacher=request.user.employee)\
            .values_list('course__pk', flat=True)
        return Course.objects.filter(Q(semester=semester), Q(teachers=request.user.employee) | Q(pk__in=courses))\
            .order_by('name')

def get_groups_for_user(request, type, course):
    """Returns groups owned by the user.

    Raises:
        Employee.DoesNotExist: If the user in the request is not an employee.
    """
    sub = Course.objects.filter(pk=course, teachers=request.user.employee)
    if request.user.is_staff or sub:
        return Group.objects.filter(type=type, course=course).order_by('teacher')
    else:
        return Group.objects.filter(type=type, course=course, teacher=request.user.employee).order_by('teacher')

def make_pages( pages, page_number ):
    if pages < 12:
        return range(1, pages)

    list = range(1, 6)
    if page_number > 8:
        list.extend( [-1])

    first = max(page_number-2, 6)
    last = min(page_number+3, pages)

    list.extend( range(first, last))

    if page_number < pages - 8:
        list.extend( [-1])

    last = min(page_number+3, pages)
    start = max(last, pages-5)
    list.extend( range(start, pages))

    return list

def edit_poll(poll, request, origin):
    poll.title = request.POST.get('title', '')
    poll.description = request.POST.get('description', '')
    poll.origin = origin
    poll.save()

    for section in SectionOrdering.objects.filter(poll=poll):
        section.delete()

    make_section_for_poll(request, poll)
