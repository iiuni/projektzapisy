# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode, smart_str
from apps.enrollment.courses.models import Course, CourseEntity

__author__ = 'maciek'


class Parser(object):
    def _convert_employee(self, name):
        _name_tables = {
            u'-00': '',
            u'-05': '',
            u'NN': '',
            u'KRYSTIAN BACŁAWSKI': 97,
            u'SEBASTIAN BALA': 11,
            u'MAŁGORZATA BIERNACKA': 74,
            u'DARIUSZ BIERNACKI': 71,
            u'MARCIN BIEŃKOWSKI': 12,
            u'WOJCIECH BOŻEJKO': 68,
            u'JAROSŁAW BYRKA': 103,
            u'WITOLD CHARATONIK': 55,
            u'BŁAŻEJ CHĘCIŃSKI': 1355,
            u'HANS DENIVELLE': 67,
            u'INSTYTUT FIZYKI DOŚWIADCZALNEJ': 1413,
            u'PATRYK FILIPIAK': 108,
            u'TOMASZ GOGACZ': 1426,
            u'PRZEMYSŁAW GOSPODARCZYK': 1658,
            u'LESZEK GROCHOLSKI': 14,
            u'ALEKSANDER IWANOW': 61,
            u'DARIUSZ JACKOWSKI': 58,
            u'TOMASZ JURDZIŃSKI': 17,
            u'PRZEMYSŁAWA KANAREK': 19,
            u'WITOLD KARCZEWSKI': 20,
            u'EMANUEL KIEROŃSKI': 23,
            u'ANDRZEJ KISIELEWICZ': 63,
            u'KORNEL KISIELEWICZ': 82,
            u'WOJCIECH KLESZOWSKI': 1334,
            u'ANTONI KOŚCIELSKI': 25,
            u'KRZYSZTOF KRUPIŃSKI': 64,
            u'JURIJ KRYAKIN': 27,
            u'STANISŁAW LEWANOWICZ': 30,
            u'KRZYSZTOF LORYŚ': 31,
            u'JERZY MARCINKOWSKI': 32,
            u'MAREK MATERZOK': 93,
            u'MARCIN MŁOTKOWSKI': 35,
            u'RAFAŁ NOWAK': 36,
            u'LESZEK PACHOLSKI': 37,
            u'KATARZYNA PALUCH': 38,
            u'WITOLD PALUSZYŃSKI': 39,
            u'MAREK PIOTRÓW': 40,
            u'ŁUKASZ PIWOWAR': 41,
            u'ZDZISŁAW PŁOSKI': 42,
            u'PAWEŁ RAJBA': 54,
            u'BARTOSZ RYBICKI': 1648,
            u'PAWEŁ RYCHLIKOWSKI': 43,
            u'PAWEŁ RZECHONEK': 44,
            u'ZDZISŁAW SPŁAWSKI': 4,
            u'GRZEGORZ STACHOWIAK': 45,
            u'MACIEJ M. SYSŁO': 1332,
            u'MAREK SZYKUŁA': 91,
            u'ROMAN WENCEL': 89,
            u'PIOTR WIECZOREK': 49,
            u'TOMASZ WIERZBICKI': 50,
            u'PIOTR WITKOWSKI': 6,
            u'PIOTR WNUK-LIPIŃSKI': 51,
            u'MIECZYSŁAW WODECKI': 52,
            u'PAWEŁ WOŹNY': 53,
            u'TOMASZ ZIELIŃSKI': 100,
            u'WIKTOR ZYCHLA': 8,
            u'ANDRZEJ ŁUKASZEWSKI': 9
        }

        return _name_tables[name]

    def _convert_day(self, day):
        _list = {
            'pn': '1',
            'wt': '2',
            u'śr': '3',
            u'Śr': '3',
            'czw': '4',
            'pi': '5'
        }

        return _list[day]

    def __init__(self, file):
        result = []
        title = ''
        groups = []

        for line in file:
            line = smart_unicode(line)
            line = line.rstrip()
            if len(line) < 2:
                continue

            elif line[1] != ' ':
                if title and groups:
                    result.append({'name': smart_str(title), 'groups': groups})
                title = self._parseTitle(line)
                groups = []
            else:
                groups.append(self._parseGroup(line))

        self.result = result

    def _parseTitle(self, title):
        return title.strip()

    def _convert_type(self, type):
        _types = {
            u'(ćwiczenia)': '2',
            u'(repetytorium)': '9',
            u'(wykład)': '1',
            u'(pracownia)': '3',
            u'(ćwicz+pracownia)': '5',
            u'(seminarium)': '6'
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
            tmpname.append(fields[i])

        name = ' '.join(tmpname)
        name = name[:-1]
        classrooms = []
        if len(fields) > i + 2:
            classrooms = str(fields[i + 2]).split(',')

        return {
            'teacher': self._convert_employee(name),
            'day': self._convert_day(day),
            'start': str(start),
            'end': str(end),
            'type': self._convert_type(type),
            'rooms': classrooms
        }

# class CourseImportForm(models.Form):
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
