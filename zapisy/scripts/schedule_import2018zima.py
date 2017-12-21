# -*- coding: utf-8 -*-


from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SCHEDULE_FILE = 'plan2018zima.txt'
LIMITS = {'1' : 300, '9' : 300, '2' : 20, '3' : 15 , '5' : 18 , '6' : 15 }

FIRST_YEAR_FRIENDLY = ['logikadlainformatykpw','analizamatematyczna','algebra','kursjezykaansiczelementamic++','wstepdoinformatyki',
                       'wstepdoprogramowania','programowanie','programowanieobiektowe','kursjezykapascal',
                       'architekturysystempwkomputerowych', 'architekturasystempwkomputerowych']
O1 = ['analizamatematyczna','algebra','logikadlainformatykpw','elementyrachunkuprawdopodobienstwa','metodyprobabilistyczneistatystyka']
O2 = ['matematykadyskretna','programowanie','analizanumeryczna','algorytmyistrukturydanych']
O3 = ['jezykiformalneiz\xa3ożonosćobliczeniowa']
Oinz = ['fizykadlainformatykpw','podstawyelektroniki,elektrotechnikiimiernictwa']
I1 = ['wstepdoinformatyki','architekturasystempwkomputerowych','architekturysystempwkomputerowych','bazydanych','systemyoperacyjne','siecikomputerowe','inżynieriaoprogramowania']
Iinz = ['systemywbudowane','podstawygrafikikomputerowej','sztucznainteligencja','komunikacjacz\xa3owiek-komputer']
FEREOL_PATH = '../../..'

SEMESTERID = 338

TECH = {
"TIETO" : 441,
"-00" : 177,
"-01" : 183,
"-05" : 193,
"-06" : 442,
"GRAŻYNA ANTCZAK" : 470,
"MAREK ARENDARCZYK" : 85,
"KRYSTIAN BACŁAWSKI" : 96,
"ANNA BARTKOWIAK" : 117,
"MARCIN BIEŃKOWSKI" : 11,
"MAŁGORZATA BIERNACKA" : 73,
"DARIUSZ BIERNACKI" : 70,
"SZYMON BONIECKI" : 196,
"WOJCIECH BOŻEJKO" : 67,
"JACEK BRONA" : 493,
"DARIUSZ BURACZEWSKI" : 488,
"JAROSŁAW BYRKA" : 102,
"BZWBK" : 516,
"WITOLD CHARATONIK" : 54,
"BŁAŻEJ CHĘCIŃSKI" : 131,
"DOROTA CHMIELEWSKA-ŁUCZAK" : 447,
"JAN CHOROWSKI" : 456,
"FILIP CHUDY" : 511,
"ANDRZEJ DĄBROWSKI" : 490,
"KRZYSZTOF DĘBICKI" : 69,
"BARTŁOMIEJ DUDEK" : 521,
"JEAN MARIE DE NIVELLE" : 66,
"INSTYTUT FIZYKI DOŚWIADCZALNEJ" : 178,
"SZYMON DUDYCZ" : 508,
"PATRYK FILIPIAK" : 107,
"JULIAN FURTAK" : 473,
"MICHAŁ GAŃCZORZ" : 510,
"PAWEŁ GARNCAREK" : 485,
"PAWEŁ GAWRYCHOWSKI" : 71,
"PRATIC GHOSAL" : 486,
"JAKUB GISMATULLIN" : 125,
"TOMASZ GOGACZ" : 191,
"MATEUSZ GOŁĘBIEWSKI" : 518,
"FRANCISZEK GOŁEK" : 124,
"PRZEMYSŁAW GOSPODARCZYK" : 449,
"LESZEK GROCHOLSKI" : 13,
"MIŁOSZ GRODZICKI" : 482,
"EWA GURBIEL" : 14,
"ALEKSANDER IWANOW" : 60,
"DARIUSZ JACKOWSKI" : 57,
"WOJCIECH JEDYNAK" : 467,
"ARTUR JEŻ" : 15,
"ŁUKASZ JEŻ" : 68,
"MICHAŁ JURCZYSZYN" : 501,
"TOMASZ JURDZIŃSKI" : 16,
"PIOTR JUREK" : 498,
"ADAM KACZMAREK" : 458,
"PRZEMYSŁAWA KANAREK" : 18,
"WITOLD KARCZEWSKI" : 19,
"MICHAŁ KARPIŃSKI" : 463,
"EMANUEL KIEROŃSKI" : 22,
"ANDRZEJ KISIELEWICZ" : 62,
"WOJCIECH KLESZOWSKI" : 116,
"ANTONI KOŚCIELSKI" : 24,
"JAKUB KOWALSKI" : 109,
"ARTUR KRASKA" : 512,
"ANDRZEJ KRAWCZYK" : 195,
"ILONA KRÓLAK" : 28,
"KRZYSZTOF KRUPIŃSKI" : 63,
"JURIJ KRYAKIN" : 26,
"ANNA KRYSTEK" : 27,
"ANDRZEJ KRZYWDA" : 120,
"MACIEJ KUCHOWICZ" : 496,
"ADAM KUNYSZ" : 483,
"WITOLD KWAŚNICKI" : 506,
"ADRIAN ŁAŃCUCKI" : 462,
"MATEUSZ LEWANDOWSKI" : 499,
"STANISŁAW LEWANOWICZ" : 29,
"RAFAŁ LIPNIEWICZ" : 504,
"ALEKSANDRA LIS" : 468,
"KRZYSZTOF LORYŚ" : 30,
"ANDRZEJ ŁUKASZEWSKI" : 8,
"MATEUSZ MACHAJ" : 475,
"JAN MARCINKOWSKI" : 519,
"JERZY MARCINKOWSKI" : 31,
"MATEUSZ MARKIEWICZ" : 522,
"MAREK MATERZOK" : 92,
"FRANCISCO MELENDEZ" : 494,
"JAKUB MICHALISZYN" : 58,
"MARCIN MŁOTKOWSKI" : 34,
"IRENEUSZ MORAWSKI" : 497,
"RAFAŁ NOWAK" : 35,
"WIOLETTA NOWAK" : 507,
"KRZYSZTOF NOWICKI" : 500,
"MAREK NOWICKI" : 491,
"MICHAŁ OLECH" : 77,
"GRZEGORZ OLENDER" : 477,
"TOMASZ OSSOWSKI" : 469,
"JAN OTOP" : 55,
"LESZEK PACHOLSKI" : 36,
"MACIEJ PACUT" : 465,
"KATARZYNA PALUCH" : 37,
"MACIEJ PALUSZYŃSKI" : 65,
"WITOLD PALUSZYŃSKI" : 38,
"KRZYSZTOF PIECUCH" : 460,
"BARBARA PIECZYRAK" : 489,
"MAREK PIOTRÓW" : 39,
"MACIEJ PIRÓG" : 515,
"ŁUKASZ PIWOWAR" : 40,
"ZDZISŁAW PŁOSKI" : 41,
"PIOTR POLESIUK" : 474,
"GABRIELA PRZESŁAWSKA" : 479,
"STANISŁAW PRZYTOCKI" : 455,
"PAWEŁ RAJBA" : 53,
"MICHAŁ RÓŻAŃSKI" : 457,
"EDYTA RUTKOWSKA-TOMASZEWSKA" : 505,
"BARTOSZ RYBICKI" : 439,
"PAWEŁ RYCHLIKOWSKI" : 42,
"PAWEŁ RZECHONEK" : 43,
"PAWEŁ SCHMIDT" : 509,
"KATARZYNA SERAFIŃSKA" : 461,
"FILIP SIECZKOWSKI" : 514,
"ANNA SMOLIŃSKA" : 452,
"MACIEJ SOBCZAK" : 130,
"PAWEŁ SOŁTYSIAK" : 91,
"KRZYSZTOF SORNAT" : 459,
"ZDZISŁAW SPŁAWSKI" : 3,
"GRZEGORZ STACHOWIAK" : 44,
"ŁUKASZ STARBA" : 520,
"DAMIAN STRASZAK" : 466,
"ADMINISTRATOR SYSTEMU" : 451,
"ANDRZEJ SZCZEPKOWICZ" : 502,
"RAFAŁ SZUKIEWICZ" : 492,
"ADAM SZUSTALEWICZ" : 82,
"MAREK SZYKUŁA" : 90,
"KAMIL TABIŚ" : 56,
"KRZYSZTOF TABISZ" : 86,
"JAKUB TARNAWSKI" : 476,
"TOMASZ TRUDERUNG" : 108,
"ROMAN URBAN" : 4,
"VACAT" : 192,
"ROMAN WENCEL" : 88,
"MONIKA WICHŁACZ" : 79,
"PIOTR WIECZOREK" : 48,
"MARCIN WIEJAK" : 517,
"TOMASZ WIERZBICKI" : 49,
"PIOTR WIÓREK" : 454,
"PIOTR WITKOWSKI" : 5,
"MARCIN WŁODARCZAK" : 1,
"PIOTR WNUK-LIPIŃSKI" : 50,
"MIECZYSŁAW WODECKI" : 51,
"KATARZYNA WODZYŃSKA" : 128,
"PAWEŁ WOŹNY" : 52,
"PAWEŁ ZAWIŚLAK" : 89,
"KLARA ZIELIŃSKA" : 484,
"WIKTOR ZYCHLA" : 7,
"NN" : 119
}

####  #####

import sys
import os
from datetime import time


from apps.enrollment.courses.models import Course, Semester, CourseEntity, Type, Group, Term, PointsOfCourseEntities, PointTypes
from apps.users.models import Student, Employee, Program

from apps.enrollment.courses.models import Classroom

import re
import logging
logger = logging.getLogger()


regex = re.compile('\s+(?P<day>pn|wt|śr|czw|pi|so|ni)\s+(?P<start_time>\d{1,2})-(?P<end_time>\d{1,2})\s+\((?P<type>wykład|repetytorium|ćwiczenia|pracownia|ćwicz\+pracownia|seminarium)\)\s+(?P<teacher>[^,]*),\s+(?P<rooms>.*)')

GROUP_TYPES = { 'wykład' : '1', 'repetytorium' : '9', 'ćwiczenia' : '2', 'pracownia' : '3' ,'ćwicz+pracownia' : '5' ,'seminarium' : '6' }

DAYS_OF_WEEK = { 'pn' : '1', 'wt' : '2', 'śr' : '3', 'czw' : '4', 'pi' : '5' , 'so' : '6', 'ni' : '7'}


def find_teacher(t):
    id = TECH.get(t, None)
    if id:
        return Employee.objects.get(id=id)
    else:
        print(("Not found: " + str(t)))
        raise Exception("Teacher not found")
        return None

def get_classroom(rooms):
    classrooms = []
    for room in rooms:
        try:
            room = int(room)
            classroom = Classroom.objects.get(number=room)
        except ValueError:
            print((bcolors.WARNING + room + ' <-not number' + bcolors.ENDC))
            classroom = room

        try:
            classroom = Classroom.objects.get(number=room)
        except ObjectDoesNotExist:
            print((bcolors.WARNING + room + ' <-notexists' + bcolors.ENDC))
            classroom = None
        if classroom:
            classrooms.append(classroom)

    return classrooms


def import_schedule(file, semester):
    types = [('Informatyczny 1','I1'),
            ('Informatyczny 2','I2'),
            ('Informatyczny inż.','Iinż'),
            ('Obowiązkowy 1','O1'),
            ('Obowiązkowy 2','O2'),
            ('Obowiązkowy 3','O3'),
            ('Obowiązkowy inż.','Oinż'),
            ('Kurs','K'), 
            ('Projekt','P'), 
            ('Seminarium','S'), 
            ('Nieinformatyczny','N'), 
            ('Wychowanie fizyczne','WF'), 
            ('Lektorat','L'), 
            ('Inne','?')]

    COURSE_TYPE = {}
    classroom = None

    course = None
    while True:
        line = file.readline()
        print(line)
        if not line:
            return
        if line.startswith('  '):
            if line.replace(' ','')=='\n':
                continue
            g = regex.match(line)
            try:
                dayOfWeek = DAYS_OF_WEEK[g.group('day')]
                start_time = time(hour=int(g.group('start_time')))
                end_time = time(hour=int(g.group('end_time')))
                rooms = g.group('rooms').replace(' ','').replace('sala','').replace('sale','').replace('\n','').split(',')
                classrooms = get_classroom(rooms)

                group_type = GROUP_TYPES[g.group('type')]
                teacher = find_teacher(g.group('teacher'))
                limit = LIMITS[group_type]
                
                t = 15*(int(g.group('end_time'))-int(g.group('start_time')))
                print(classrooms)                    
                if group_type=='1':    
                    group = Group.objects.get_or_create(course=course,
                                                        teacher=teacher,
                                                        type=group_type,
                                                        limit=limit)[0]
                else:
                    group = Group.objects.create(course=course,
                                                        teacher=teacher,
                                                        type=group_type,
                                                        limit=limit)
                term = Term.objects.create(dayOfWeek=dayOfWeek,
                                           start_time=start_time,
                                           end_time=end_time,
                                           classroom=classroom,
                                           group=group)
                term.classrooms = classrooms
                term.save()
                
            except AttributeError:
                print(('Error: line`'+line+'\' don\'t match regexp.'))

        elif line.startswith(' '):
            if line==' \n':
                continue
            
            name = line.strip()
            try:
                course = get_course(name)
            except Exception as e:
                print(('Error during creating course:%s. \nError: %s ' % (name, e)))
                break

        else:
            continue

def get_semester():
    return Semester.objects.get(id=SEMESTERID)

def get_course(name):
    try:
        ce = CourseEntity.objects.get(name_pl__iexact = name)
    except ObjectDoesNotExist:
        print((bcolors.FAIL+'   [not exists error] '+name+bcolors.ENDC))
    except MultipleObjectsReturned:
        print((bcolors.FAIL+'   [multiple objects error (took newest,for vote)] '+name+bcolors.ENDC))
        ce = CourseEntity.objects.filter(name_pl__iexact = name,status=2).order_by('-id')[0]

    return Course.objects.get(entity=ce.id,semester=SEMESTERID)

# for running scheduleimport.py from tests
def run_test(TEST_SCHEDULE_FILE, test_przedmioty, TEST_TECH, TEST_SEMESTERID):
    global SCHEDULE_FILE, przedmioty, TECH, SEMESTERID
    SCHEDULE_FILE = TEST_SCHEDULE_FILE
    przedmioty = test_przedmioty
    TECH = TEST_TECH
    SEMESTERID = TEST_SEMESTERID
    run()

def get_courses_ids(semester):
    cc = Course.objects.filter(semester=semester)
    for c in cc:
        print(('"' + c.name.upper() + '" : '+ str(c.id) + ","))

def get_employers_ids():
    ee = Employee.objects.filter(status = 0)
    for e in ee:
        print(('"' + e.get_full_name().upper() + '" : '+ str(e.id) + ","))        

def run():
    semester = get_semester()
    # get_courses_ids(semester)
    # get_employers_ids()
    print(('Przenosimy na semestr <%s>' % semester))
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

