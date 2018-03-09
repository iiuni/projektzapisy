import os
from django.db import transaction
from django.template.defaultfilters import slugify
from lxml import etree
from django.conf import settings
from apps.enrollment.courses.models import Semester, Group, Course, Term, \
     CourseEntity, Type, Classroom
from apps.users.models import Employee

XSCHEMA = os.path.join(settings.BASE_DIR, 'enrollment/courses/admin/xml/semesterschedule.xsd')


@transaction.atomic
def import_semester_schedule(xmlfile):
    """ This function parses XML file containing complete schedule of semester (courses, grups, terms,
        teachers, etc.). The file is validated with XSCHEMA.

        xmlfile - path to XML file or file object
    """

    def get_teacher(el_teacher):
        """ This function parses <teacher> element and returns existing in database Employee object """

        name = el_teacher.find('name').text
        surname = el_teacher.find('surname').text

        try:
            employee = Employee.objects.get(first_name=name,
                                        last_name=surname
                                        )
        except Employee.DoesNotExist:
            raise Employee.DoesNotExist('Employee name="%s"  surname="%s" does not exist' % (name, surname))

        return employee

    def get_teachers(el_teachers):
        """ This function parses <teachers> element and returns list of Employees objects """

        teachers = []

        for el_teacher in el_teachers:
            teachers.append(get_teacher(el_teacher))

        return teachers

    def create_course(el_course, semester):
        """ This function parses <course> element """

        teachers = get_teachers(el_course.find('teachers'))

        name = el_course.find('name').text
        entity = CourseEntity.objects.get_or_create(name=name)[0]
        slug = slugify(semester.year + '_' + name)
        # TODO: nie testowane:
        sub_type = Type.objects.get_or_create(name=el_course.find('type').text, meta_type=False)[0]
        desc = el_course.find('desc').text
        lectures = el_course.find('lectures').text
        exercises = el_course.find('exercises').text
        labs = el_course.find('laboratories').text

        course = Course.objects.create(entity=entity,
                                         name=name,
                                         slug=slug,
                                         semester=semester,
                                         type=sub_type,
                                         description=desc,
                                         lectures=lectures,
                                         exercises=exercises,
                                         laboratories=labs
                                         )

        course.teachers = teachers
        course.save()

        create_groups(el_course.find('groups'), course)

    def create_groups(el_groups, course):
        """ This function parses <groups> element """

        for el_group in el_groups:
            el_teacher = el_group.find('teacher')

            if el_teacher:
                teacher = get_teacher(el_teacher)
            else:
                teacher = None

            el_type_text = el_group.find('type').text

            if el_type_text == 'lecture':
                gr_type = '1'
            elif el_type_text == 'exercise':
                gr_type = '2'
            elif el_type_text == 'laboratory':
                gr_type = '3'
            elif el_type_text == 'exercise_adv':
                gr_type = '4'
            elif el_type_text == 'exer_lab':
                gr_type = '5'
            elif el_type_text == 'seminar':
                gr_type = '6'
            elif el_type_text == 'language':
                gr_type = '7'
            elif el_type_text == 'sport':
                gr_type = '8'

            limit = el_group.find('limit').text

            group = Group.objects.create(course=course,
                         teacher=teacher,
                         type=gr_type,
                         limit=limit
                         )

            create_terms(el_group.find('terms'), group)


    def create_terms(el_terms, group):
        """ This function parses <terms> element and returns list of Terms objects """
        terms = []

        for el_term in el_terms:
            el_day_text = el_term.find('day').text

            if(el_day_text == 'monday'):
                day = '1'
            elif(el_day_text == 'tuesday'):
                day = '2'
            elif(el_day_text == 'wednesday'):
                day = '3'
            elif(el_day_text == 'thursday'):
                day = '4'
            elif(el_day_text == 'friday'):
                day = '5'
            elif(el_day_text == 'saturday'):
                day = '6'
            elif(el_day_text == 'sunday'):
                day = '7'

            start_time = el_term.find('startTime').text
            end_time = el_term.find('endTime').text
            classroom = Classroom.objects.get_or_create(number=el_term.find('room').text
                                                        )[0]

            terms.append(Term.objects.create(dayOfWeek=day,
                                                                                 start_time=start_time,
                                                                                 end_time=end_time,
                                                                                 classroom=classroom,
                                                                                 group=group
                                                                                 )
                         )

        return terms

    schema = etree.XMLSchema(file=XSCHEMA)
    events = etree.iterparse(xmlfile,
                             remove_blank_text=True,
                             remove_comments=True,
                             events=('start','end'),
                             schema=schema
                             )

    new_sem = False

    for event, element in events:
        if event == 'start' and element.tag == 'semester':
            new_sem = True
        elif new_sem == True and event == 'end' and element.tag == 'year':
            sem_year = element.text
        elif new_sem == True and event == 'end' and element.tag == 'type':
            if element.text == 'winter':
                sem_type = Semester.TYPE_WINTER
            elif element.text == 'summer':
                sem_type = Semester.TYPE_SUMMER

            new_sem = False

            semester = Semester.objects.create(visible=False,
                                               year=sem_year,
                                               type=sem_type)

        elif event == 'end' and element.tag == 'course':
            create_course(element, semester)
            element.clear()

            while element.getprevious() is not None:
                del element.getparent()[0]
