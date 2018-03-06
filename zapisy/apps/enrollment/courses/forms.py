from django import forms
from django.core.exceptions import ObjectDoesNotExist
from apps.enrollment.courses.models import Course, CourseEntity

__author__ = 'maciek'


class Parser(object):
    def _convert_employee(self, name):
        _name_tables = {
            '-00' : '',
            '-05': '',
            'NN': '',
            'KRYSTIAN BACŁAWSKI': 97,
            'SEBASTIAN BALA': 11,
            'MAŁGORZATA BIERNACKA': 74,
            'DARIUSZ BIERNACKI': 71,
            'MARCIN BIEŃKOWSKI': 12,
            'WOJCIECH BOŻEJKO': 68,
            'JAROSŁAW BYRKA': 103,
            'WITOLD CHARATONIK':55,
            'BŁAŻEJ CHĘCIŃSKI': 1355,
            'HANS DENIVELLE': 67,
            'INSTYTUT FIZYKI DOŚWIADCZALNEJ': 1413,
            'PATRYK FILIPIAK': 108,
            'TOMASZ GOGACZ': 1426,
            'PRZEMYSŁAW GOSPODARCZYK':1658,
            'LESZEK GROCHOLSKI':14,
            'ALEKSANDER IWANOW':61,
            'DARIUSZ JACKOWSKI':58,
            'TOMASZ JURDZIŃSKI':17,
            'PRZEMYSŁAWA KANAREK':19,
            'WITOLD KARCZEWSKI':20,
            'EMANUEL KIEROŃSKI':23,
            'ANDRZEJ KISIELEWICZ':63,
            'KORNEL KISIELEWICZ':82,
            'WOJCIECH KLESZOWSKI':1334,
            'ANTONI KOŚCIELSKI':25,
            'KRZYSZTOF KRUPIŃSKI':64,
            'JURIJ KRYAKIN':27,
            'STANISŁAW LEWANOWICZ':30,
            'KRZYSZTOF LORYŚ':31,
            'JERZY MARCINKOWSKI':32,
            'MAREK MATERZOK':93,
            'MARCIN MŁOTKOWSKI':35,
            'RAFAŁ NOWAK':36,
            'LESZEK PACHOLSKI':37,
            'KATARZYNA PALUCH':38,
            'WITOLD PALUSZYŃSKI':39,
            'MAREK PIOTRÓW':40,
            'ŁUKASZ PIWOWAR':41,
            'ZDZISŁAW PŁOSKI':42,
            'PAWEŁ RAJBA':54,
            'BARTOSZ RYBICKI':1648,
            'PAWEŁ RYCHLIKOWSKI':43,
            'PAWEŁ RZECHONEK':44,
            'ZDZISŁAW SPŁAWSKI':4,
            'GRZEGORZ STACHOWIAK':45,
            'MACIEJ M. SYSŁO':1332,
            'MAREK SZYKUŁA':91,
            'ROMAN WENCEL':89,
            'PIOTR WIECZOREK':49,
            'TOMASZ WIERZBICKI':50,
            'PIOTR WITKOWSKI':6,
            'PIOTR WNUK-LIPIŃSKI':51,
            'MIECZYSŁAW WODECKI':52,
            'PAWEŁ WOŹNY':53,
            'TOMASZ ZIELIŃSKI':100,
            'WIKTOR ZYCHLA':8,
            'ANDRZEJ ŁUKASZEWSKI':9
        }

        return _name_tables[name]


    def _convert_day(self, day):
        _list = {
            'pn': '1',
            'wt': '2',
            'śr': '3',
            'Śr': '3',
            'czw': '4',
            'pi': '5'
        }

        return _list[day]


    def __init__(self, file):
        result = []
        title = ''
        groups = []

        for line in file:
            line = str(line)
            line = line.rstrip()
            if len(line) < 2:
                continue

            elif line[1] != ' ':
                if title and groups:
                    result.append( {'name': smart_str(title), 'groups': groups} )
                title = self._parseTitle(line)
                groups = []
            else:
                groups.append( self._parseGroup(line) )

        self.result = result

    def _parseTitle(self, title):
        return title.strip()

    def _convert_type(self, type):
        _types = {
           '(ćwiczenia)': '2',
           '(repetytorium)': '9',
           '(wykład)': '1',
           '(pracownia)': '3',
           '(ćwicz+pracownia)': '5',
           '(seminarium)': '6'
        }

        return _types[type]

    def get_result(self):
        return self.result

    def _parseGroup(self, line):

        row = line.strip()
        fields = row.split()
        day = fields[0]
        start, end = fields[1].split('-')
        type = fields[2]
        tmpname = [fields[3]]
        i = 3
        while fields[i][-1] != ',':
            i += 1
            tmpname.append( fields[i] )

        name = ' '.join(tmpname)
        name = name[:-1]
        classrooms = []
        if len(fields) > i+2:
            classrooms = str(fields[i+2]).split(',')


        return {
            'teacher': self._convert_employee(name),
            'day' : self._convert_day(day),
            'start': str(start),
            'end': str(end),
            'type': self._convert_type(type),
            'rooms': classrooms
        }

#class CourseImportForm(models.Form):
#
#    class Meta:
#        fiedls = ['e']
#        model = Course


class ImportForm(object):

    def create_from_dict(self, courses):

        for course in courses:
            try:
                c = Course.objects.get(entity__name__iexact=course['name'])
            except ObjectDoesNotExist:
                c = Course()

            for group in courses['groups']:
                gr = Group()
                gr.course = c
                gr.type = group['type']
                gr.teacher_id = group['teacher']
                """
                group -> termin, sala, osoba
              """





"""
    Jak to działa?

    wczytujemy plik -> tworzymy stronę do akceptacji (form)

    Wczytana nazwa: Znaleziony kurs (link) / select
    [ukryte pole tekstowe z grupami]
    wypisane grupy

"""


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['entity']

    def save(self, commit=True):

        course = super(CourseForm, self).save(commit=False)
        course.information = course.entity.information

        if commit:
            course.save()

        return course