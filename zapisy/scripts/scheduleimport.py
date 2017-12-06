# -*- coding: utf-8 -*-


from django.core.exceptions import ObjectDoesNotExist

SCHEDULE_FILE = 'plan.txt'
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

SEMESTERID = 333

przedmioty = {"ALGEBRA": 3457,
  "ALGORYTMICZNA TEORIA GIER": 3458,
 "ALGORYTMY EWOLUCYJNE": 3459,
 "ALGORYTMY I STRUKTURY DANYCH (M)": 3460,
 "ALGORYTMY ROZPROSZONE": 3461,
 "ANALIZA DANYCH I WARIANCJI": 3462,
 "ARCHITEKTURY SYSTEMoW KOMPUTEROWYCH": 3463,
 "BAZY DANYCH": 3464,
 "DIGITIZING THE REAL WORLD": 3465,
 "FIZYKA DLA INFORMATYKoW": 3466,
 "GEOMETRIA OBLICZENIOWA": 3467,
 "HURTOWNIE DANYCH I DATA MINING": 3468,
 "J ZYKI FORMALNE I ZlOzONOsc OBLICZENIOWA": 3469,
 "KRYPTOGRAFIA": 3470,
 "KURS J ZYKA C++": 3471,
 "KURS MODELOWANIA 3D I WIZUALIZACJI W PROGRAMIE SKETCHUP": 3472,
 "KURS PRACY W SYSTEMIE LINUX": 3473,
 "KURS PROGRAMOWANIA POD WINDOWS W TECHNOLOGII .NET": 3474,
 "KURS PROJEKTOWANIA APLIKACJI Z BAZAMI DANYCH": 3475,
 "KURS XML": 3476,
 "KURS: NOWOCZESNE J ZYKI PRZETWARZANIA DANYCH: PYTHON, R I MATLAB": 3477,
 "KURS: PRACTICAL C# ENTERPRISE SOFTWARE DEVELOPMENT": 3478,
 "KURS: PRAKTYCZNE ASPEKTY ROZWOJU OPROGRAMOWANIA": 3479,
 "KURS: PROGRAMOWANIE W C++": 3480,
 "MATEMATYCZNE METODY GRAFIKI KOMPUTEROWEJ": 3481,
 "METODY OPTYMALIZACJI": 3482,
 "METODY PROGRAMOWANIA": 3483,
 "METODY SZTUCZNEJ INTELIGENCJI W ZARZaDZANIU I STEROWANIU PRODUKCJ": 3484,
 "MODELOWANIE ZJAWISK PRZYRODNICZYCH": 3485,
 "OPTYMALIZACJA KOMBINATORYCZNA": 3486,
 "PRAWO I PODATKI W BIZNESIE": 3487,
 "PROGRAMOWANIE OBIEKTOWE": 3488,
 "PROJEKTOWANIE OBIEKTOWE OPROGRAMOWANIA": 3489,
 "RACHUNEK PRAWDOPODOBIEnSTWA I STATYSTYKA": 3490,
 "REALISTYCZNA GRAFIKA KOMPUTEROWA": 3491,
 "SEMINARIUM ALGORYTMICZNE 2016": 3492,
 "SEMINARIUM Z SYSTEMoW": 3493,
 "SEMINARIUM: ALGORYTMY W KOMUNIKACJI BEZPRZEWODOWEJ": 3494,
 "SEMINARIUM: GRAFIKA KOMPUTEROWA 2016": 3495,
 "SEMINARIUM: INzYNIERIA OPROGRAMOWANIA": 3496,
 "SEMINARIUM: SIECI NEURONOWE I STATYSTYKA": 3497,
 "SEMINARIUM: TESTOWANIE OPROGRAMOWANIA": 3498,
 "SEMINARIUM: ZAAWANSOWANE PROGRAMOWANIE FUNKCYJNE": 3499,
 "SIECI KOMPUTEROWE": 3500,
 "SYNTEZA MOWY": 3501,
 "SYSTEMY ROZPROSZONE": 3502,
 "SZTUCZNA INTELIGENCJA": 3503,
 "TEORETYCZNE PODSTAWY JeZYKoW PROGRAMOWANIA": 3504,
 "TESTOWANIE OPROGRAMOWANIA": 3505,
 "THEOREM PROVING": 3506,
 "ZAJeCIA Z KRYTYCZNEGO MYsLENIA": 3507,
 "SYSTEMY KOMPUTEROWE": 3508
}


TECH = { "KRYSTIAN BAClAWSKI": 96,
 "MAlGORZATA BIERNACKA":  73,
 "DARIUSZ BIERNACKI":  70,
 "MARCIN BIEnKOWSKI":  11,
 "SZYMON BONIECKI":  73,
 "JAROSlAW BYRKA":  102,
 "WITOLD CHARATONIK":  54,
 "JAN CHOROWSKI":  456,
 "HANS DENIVELLE":  66,
 "KRZYSZTOF DeBICKI":  69,
 "AGNIESZKA FALEnSKA":464,
 "PATRYK FILIPIAK":  107,
 "INSTYTUT FIZYKI DOsWIADCZALNEJ":  178,
 "PRZEMYSlAW GOSPODARCZYK":  449,
 "LESZEK GROCHOLSKI":  13,
 "TOMASZ JURDZInSKI":  16,
 "ADAM KACZMAREK": 458,
 "PRZEMYSlAWA KANAREK": 18,
 "WITOLD KARCZEWSKI": 19,
 "MICHAl KARPInSKI": 463,
 "EMANUEL KIEROnSKI": 22,
 "WOJCIECH KLESZOWSKI": 116,
 "JAKUB KOWALSKI": 109,
 "ANTONI KOsCIELSKI": 24,
 "JURIJ KRYAKIN": 26,
 "ANDRZEJ KRZYWDA":  120,
 "ILONA KRoLAK":  28,
 "STANISlAW LEWANOWICZ":  29,
 "KRZYSZTOF LORYs":  30,
 "JERZY MARCINKOWSKI": 31,
 "MAREK MATERZOK": 92,
 "MARCIN MlOTKOWSKI": 34,
 "RAFAl NOWAK": 35,
 "LESZEK PACHOLSKI":  36,
 "MACIEJ PACUT": 465,
 "KATARZYNA PALUCH":  37,
 "MACIEJ PALUSZYnSKI": 65,
 "WITOLD PALUSZYnSKI": 38,
 "KRZYSZTOF PIECUCH": 460,
 "MAREK PIOTRoW": 39,
 "lUKASZ PIWOWAR": 40,
 "BARTOSZ RYBICKI": 439,
 "ZDZISlAW PlOSKI": 41,
 "PAWEl RAJBA": 53,
 "PAWEl RYCHLIKOWSKI": 42,
 "PAWEl RZECHONEK":  43,
 "MICHAl RozAnSKI": 457,
 "KATARZYNA SERAFInSKA": 461,
 "KRZYSZTOF SORNAT": 459,
 "PAWEl SOlTYSIAK": 91,
 "ZDZISlAW SPlAWSKI": 3,
 "GRZEGORZ STACHOWIAK": 44,
 "DAMIAN STRASZAK": 466,
 "MACIEJ M. SYSlO": 114,
 "ADAM SZUSTALEWICZ": 82,
 "MAREK SZYKUlA": 90,
 "KRZYSZTOF TABISZ": 86,
 "PIOTR WIECZOREK": 48,
 "TOMASZ WIERZBICKI": 49,
 "PIOTR WITKOWSKI": 5,
 "PIOTR WNUK-LIPInSKI":  50,
 "MIECZYSlAW WODECKI": 51,
 "PAWEl WOzNY": 52,
 "WIKTOR ZYCHLA": 7,
 "ANDRZEJ lUKASZEWSKI": 8,
  "ADRIAN lAnCUCKI": 462,
  "ROMAN URBAN": 4,
  "BARTOSZ TROJAN": 87,
  "PAWEl LASKOs-GRABOWSKI": 481,
  "ARTUR JEz": 15,
  "URSZULA BANASZCZAK-SOROKA": 478,
 "PATIK GHOSAL": 486,
 "GABRIELA PRZESlAWSKA": 479,
 "PIOTR POLESIUK": 474,
         "ADAM KUNYSZ": 483,
"lUKASZ JEz": 68,
"JAKUB MICHALISZYN": 58,
"FRANCISCO MELENDEZ": 494,
"JACEK BRONA": 493,
"MAREK NOWICKI": 491,
"BARBARA PIECZYRAK": 489,
"KRZYSZTOF NOWICKI": 500,
"JAN OTOP":55,
"KLARA ZIELInSKA": 48
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


regex = re.compile('\s+(?P<day>pn|wt|sr|czw|pi|so|ni)\s+(?P<start_time>\d{1,2})-(?P<end_time>\d{1,2})\s+\((?P<type>wyklad|repetytorium|cwiczenia|pracownia|cwicz\+pracownia|seminarium)\)\s+(?P<teacher>[^,]*),\s+(?P<rooms>.*)')

GROUP_TYPES = { 'wyklad' : '1', 'repetytorium' : '9', 'cwiczenia' : '2', 'pracownia' : '3' ,'cwicz+pracownia' : '5' ,'seminarium' : '6' }

DAYS_OF_WEEK = { 'pn' : '1', 'wt' : '2', 'sr' : '3', 'czw' : '4', 'pi' : '5' , 'so' : '6', 'ni' : '7'}


def find_teacher(t):
    id = TECH.get(t, None)
    if id:
        return Employee.objects.get(id=id)
    else:
        return None

def get_classroom(rooms):
    classrooms = []
    for room in rooms:
        try:
            if room.replace(' ','')=='':
                classroom = None
            else:
                classroom = Classroom.objects.get(number=room)
        except ObjectDoesNotExist:
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
                print('Error: line`'+line+'\' don\'t match regexp.')

        elif line.startswith(' '):
            if line==' \n':
                continue
            
            name = line.strip()
            try:
                course = get_course(name)
            except Exception as e:
                print('Error during creating course:%s. \nError: %s ' % (name, e))
                break

        else:
            continue

def get_semester():
    return Semester.objects.get(id=SEMESTERID)

def get_course(name):
    return Course.objects.get(id=przedmioty[name])

# for running scheduleimport.py from tests
def run_test(TEST_SCHEDULE_FILE, test_przedmioty, TEST_TECH, TEST_SEMESTERID):
    global SCHEDULE_FILE, przedmioty, TECH, SEMESTERID
    SCHEDULE_FILE = TEST_SCHEDULE_FILE
    przedmioty = test_przedmioty
    TECH = TEST_TECH
    SEMESTERID = TEST_SEMESTERID
    run()

def run():
    semester = get_semester()
    print('Przenosimy na semestr <%s>' % semester)
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

