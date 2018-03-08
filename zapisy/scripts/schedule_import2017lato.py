

from django.core.exceptions import ObjectDoesNotExist

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SCHEDULE_FILE = 'plan2017lato.txt'
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

SEMESTERID = 337

przedmioty = {
"ALGEBRA" : 3570,
"ALGORYTMY APROKSYMACYJNE" : 3571,
"ALGORYTMY EWOLUCYJNE" : 3572,
"ALGORYTMY I STRUKTURY DANYCH (M)" : 3573,
"ALGORYTMY PROBABILISTYCZNE" : 3574,
"ANALIZA MATEMATYCZNA 2" : 3575,
"ANALIZA NUMERYCZNA 2" : 3576,
"ANALIZA PROGRAMÓW KOMPUTEROWYCH" : 3577,
"ARCHITEKTURY SYSTEMÓW KOMPUTEROWYCH" : 3578,
"BAZY DANYCH" : 3579,
"FIZYKA DLA INFORMATYKÓW" : 3580,
"JĘZYKI FORMALNE I ZŁOŻONOŚĆ OBLICZENIOWA" : 3582,
"KOMPRESJA DANYCH" : 3581,
"KRYPTOGRAFIA" : 3583,
"KSZTAŁTOWANIE ŚCIEŻKI AKADEMICKO-ZAWODOWEJ" : 3631,
"KURS: BEZPIECZEŃSTWO APLIKACJI" : 3584,
"KURS: INFORMATYKA W BANKOWOŚCI" : 3585,
"KURS JĘZYKA C++" : 3589,
"KURS JĘZYKA LUA" : 3590,
"KURS MODELOWANIA 3D I WIZUALIZACJI W PROGRAMIE SKETCHUP" : 3591,
"KURS: PRAKTYCZNE ASPEKTY ROZWOJU OPROGRAMOWANIA" : 3586,
"KURS PROGRAMOWANIA POD WINDOWS W TECHNOLOGII .NET" : 3593,
"KURS: PROGRAMOWANIE W C++" : 3587,
"KURS PROJEKTOWANIA APLIKACJI Z BAZAMI DANYCH" : 3594,
"KURS XML" : 3595,
"KURS: ZAAWANSOWANE TECHNOLOGIE JAVY" : 3588,
"METODY OPTYMALIZACJI" : 3596,
"METODY PROGRAMOWANIA" : 3597,
"METODY SZTUCZNEJ INTELIGENCJI W ZARZĄDZANIU I STEROWANIU PRODUKCJĄ" : 3598,
"MODELOWANIE ZJAWISK PRZYRODNICZYCH" : 3599,
"O EKONOMII I GOSPODARCE INACZEJ" : 3600,
"PEWNE ALGORYTMY SYMBOLICZNE" : 3601,
"PODSTAWY TECHNOLOGII BITCOIN" : 3626,
"PROGRAMOWANIE OBIEKTOWE" : 3602,
"PROJEKT DYPLOMOWY" : 3603,
"PROJEKTOWANIE OBIEKTOWE OPROGRAMOWANIA" : 3607,
"PROJEKT: ROZWÓJ SYSTEMU ZAPISÓW" : 3606,
"PROJEKT: SYSTEM OPERACYJNY MIMIKER" : 3605,
"PROJEKT ZESPOŁOWY: SILNIK UNITY3D I WIRTUALNA RZECZYWISTOŚĆ 2" : 3604,
"PRZETWARZANIE OBRAZÓW" : 3608,
"RACHUNEK PRAWDOPODOBIEŃSTWA I STATYSTYKA" : 3609,
"SEMINARIUM ALGORYTMICZNE 2017" : 3616,
"SEMINARIUM APROKSYMACYJNO-OPTYMALIZACYJNO-KOMBINATORYCZNE 2" : 3612,
"SEMINARIUM: ARCHITEKTURY SKALOWALNE" : 3635,
"SEMINARIUM: CERTYFIKACJA PROGRAMÓW W SYSTEMIE COQ" : 3615,
"SEMINARIUM: EFEKTY W PROGRAMOWANIU FUNKCYJNYM" : 3618,
"SEMINARIUM: INŻYNIERIA OPROGRAMOWANIA" : 3613,
"SEMINARIUM: ROZWIĄZYWANIE WIĘZÓW W PRAKTYCE" : 3611,
"SEMINARIUM: SEMANTYKI, SYSTEMY TYPÓW I ANALIZY STATYCZNE DLA JAVASCRIPTU" : 3619,
"SEMINARIUM: TESTOWANIE OPROGRAMOWANIA" : 3614,
"SEMINAR: MODULAR REASONING ABOUT PROGRAMS" : 3617,
"SIECI KOMPUTEROWE" : 3620,
"SIECI NEURONOWE" : 3621,
"SYNTEZA MOWY" : 3622,
"SYSTEMY KOMPUTEROWE" : 3623,
"SYSTEMY ROZPROSZONE" : 3624,
"SZTUCZNA INTELIGENCJA W GRACH: PROJEKTY ZESPOŁOWE" : 3625,
"TEORETYCZNE PODSTAWY JĘZYKÓW PROGRAMOWANIA" : 3627,
"TEORIA PROGRAMOWANIA LINIOWEGO I CAŁKOWITOLICZBOWEGO" : 3628,
"TESTOWANIE OPROGRAMOWANIA" : 3629,
"TEXT MINING" : 3630,
"WNIOSKOWANIE STATYSTYCZNE" : 3632,
"WSTĘP DO RACHUNKU LAMBDA" : 3633,
"ZASADY KRYTYCZNEGO MYŚLENIA" : 3634
}

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
"HANS DENIVELLE" : 66,
"INSTYTUT FIZYKI DOŚWIADCZALNEJ" : 178,
"SZYMON DUDYCZ" : 508,
"PATRYK FILIPIAK" : 107,
"JULIAN FURTAK" : 473,
"MICHAŁ GAŃCZORZ" : 510,
"PAWEŁ GARNCAREK" : 485,
"PAWEŁ GAWRYCHOWSKI" : 71,
"PRATIK GHOSAL" : 486,
"JAKUB GISMATULLIN" : 125,
"TOMASZ GOGACZ" : 191,
"MATEUSZ GOŁĘBIEWSKI" : 518,
"FRANCISZEK GOŁEK" : 124,
"PRZEMYSŁAW GOSPODARCZYK" : 449,
"LESZEK GROCHOLSKI" : 13,
"MIŁOSZ GRODZICKI" : 482,
"EWA GURBIEL" : 14,
"ALEKSANDER IWANOW" : 60,
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
"JERZY MARCINKOWSKI" : 31,
"MAREK MATERZOK" : 92,
"FRANCHO MELENDEZ" : 494,
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

# TECH = {
# "TIETO " : 441,
# "-00" : 177,
# "-01" : 183,
# "-05" : 193,
# "-06" : 442,
# "GRAŻYNA ANTCZAK" : 470,
# "MAREK ARENDARCZYK" : 85,
# "KRYSTIAN BACŁAWSKI" : 96,
# "SEBASTIAN BALA" : 10,
# "URSZULA BANASZCZAK-SOROKA" : 478,
# "ANDRZEJ BARANOWSKI" : 121,
# "SŁAWOMIR BARĆ" : 93,
# "ANNA BARTKOWIAK" : 117,
# "BOGDAN BARWIŃSKI" : 123,
# "DIGVIJAY BHARAT" : 101,
# "MARCIN BIEŃKOWSKI" : 11,
# "MAŁGORZATA BIERNACKA" : 73,
# "DARIUSZ BIERNACKI" : 70,
# "SZYMON BONIECKI" : 196,
# "WOJCIECH BOŻEJKO" : 67,
# "MARCIN BRODZIAK" : 9,
# "JACEK BRONA" : 493,
# "DARIUSZ BURACZEWSKI" : 488,
# "JAROSŁAW BYRKA" : 102,
# "WITOLD CHARATONIK" : 54,
# "BŁAŻEJ CHĘCIŃSKI" : 131,
# "DOROTA CHMIELEWSKA-ŁUCZAK" : 447,
# "JAN CHOROWSKI" : 456,
# "TOMASZ CICHOCKI" : 76,
# "KRZYSZTOF CZARNECKI" : 83,
# "ANDRZEJ DĄBROWSKI" : 490,
# "MONIKA DEMICHOWICZ" : 2,
# "HANS DENIVELLE" : 66,
# "KRZYSZTOF DĘBICKI" : 69,
# "MAGDALENA DĘBSKA" : 180,
# "DANIEL DOBRIJAŁOWSKI" : 445,
# "ARKADIUSZ DOMAGAŁA" : 118,
# "INSTYTUT FIZYKI DOŚWIADCZALNEJ" : 178,
# "ANDRZEJ DYBCZYŃSKI" : 97,
# "AGNIESZKA FALEŃSKA" : 464,
# "PATRYK FILIPIAK" : 107,
# "JULIAN FURTAK" : 473,
# "PAWEŁ GARNCAREK" : 485,
# "PAWEŁ GAWRYCHOWSKI" : 71,
# "PRATIK GHOSAL" : 486,
# "JAKUB GISMATULLIN" : 125,
# "PRZEMYSŁAW GODOWSKI" : 181,
# "TOMASZ GOGACZ" : 191,
# "PIOTR GOGOL" : 59,
# "FRANCISZEK GOŁEK" : 124,
# "ZBIGNIEW GOŁĘBIEWSKI" : 12,
# "PRZEMYSŁAW GOSPODARCZYK" : 449,
# "LESZEK GROCHOLSKI" : 13,
# "MIŁOSZ GRODZICKI" : 482,
# "ANDRZEJ GRZESZCZAK" : 448,
# "EWA GURBIEL" : 14,
# "ALEKSANDER IWANOW" : 60,
# "DARIUSZ JACKOWSKI" : 57,
# "ELŻBIETA JAKUBCZAK" : 453,
# "WOJCIECH JEDYNAK" : 467,
# "JAKUB JERNAJCZYK" : 61,
# "JULIAN JEZIORO" : 94,
# "ARTUR JEŻ" : 15,
# "ŁUKASZ JEŻ" : 68,
# "MICHAŁ JURCZYSZYN" : 501,
# "TOMASZ JURDZIŃSKI" : 16,
# "PIOTR JUREK" : 498,
# "ADAM KACZMAREK" : 458,
# "MICHALIS KAMBURELIS" : 17,
# "PRZEMYSŁAWA KANAREK" : 18,
# "WITOLD KARCZEWSKI" : 19,
# "MICHAŁ KARPIŃSKI" : 463,
# "MAGDALENA KASZUBA-ROGÓRZ" : 20,
# "PAWEŁ KELLER" : 21,
# "EMANUEL KIEROŃSKI" : 22,
# "ANDRZEJ KISIELEWICZ" : 62,
# "KORNEL KISIELEWICZ" : 81,
# "WOJCIECH KLESZOWSKI" : 116,
# "EWA KOŁCZYK" : 23,
# "ANTONI KOŚCIELSKI" : 24,
# "MACIEJ KOTOWICZ" : 446,
# "JAKUB KOWALSKI" : 109,
# "ANDRZEJ KRAWCZYK" : 195,
# "ILONA KRÓLAK" : 28,
# "HELENA KRUPICKA" : 25,
# "KRZYSZTOF KRUPIŃSKI" : 63,
# "JURIJ KRYAKIN" : 26,
# "ANNA KRYSTEK" : 27,
# "ANDRZEJ KRZYWDA" : 120,
# "MACIEJ KUCHOWICZ" : 496,
# "ADAM KUNYSZ" : 483,
# "WITOLD KWAŚNICKI" : 506,
# "PAWEŁ LASKOŚ-GRABOWSKI" : 481,
# "MATEUSZ LEWANDOWSKI" : 499,
# "STANISŁAW LEWANOWICZ" : 29,
# "RAFAŁ LIPNIEWICZ" : 504,
# "ALEKSANDRA LIS" : 468,
# "KRZYSZTOF LORYŚ" : 30,
# "ADRIAN ŁAŃCUCKI" : 462,
# "JAKUB ŁOPUSZAŃSKI" : 72,
# "ANDRZEJ ŁUKASZEWSKI" : 8,
# "MATEUSZ MACHAJ" : 475,
# "MARTA MAKUCH-PASZKIEWICZ" : 84,
# "JERZY MARCINKOWSKI" : 31,
# "LESZEK MARKOWSKI" : 450,
# "MAREK MATERZOK" : 92,
# "ALEKSANDER MĄDRY" : 33,
# "FRANCHO MELENDEZ" : 494,
# "JAKUB MICHALISZYN" : 58,
# "JAN MIODEK" : 64,
# "MARCIN MŁOTKOWSKI" : 34,
# "WOJCIECH MŁOTKOWSKI" : 110,
# "IRENEUSZ MORAWSKI" : 497,
# "MICHAŁ MOSKAL" : 32,
# "MACIEJ NAWROCKI" : 104,
# "NN" : 112,
# "NN?" : 444,
# "NN2" : 115,
# "NOKIA" : 184,
# "RAFAŁ NOWAK" : 35,
# "WIOLETTA NOWAK" : 507,
# "KRZYSZTOF NOWICKI" : 500,
# "MAREK NOWICKI" : 491,
# "MICHAŁ OLECH" : 77,
# "GRZEGORZ OLENDER" : 477,
# "KAROLINA OLSZEWSKA" : 480,
# "TOMASZ OSSOWSKI" : 469,
# "JAN OTOP" : 55,
# "LESZEK PACHOLSKI" : 36,
# "MACIEJ PACUT" : 465,
# "KATARZYNA PALUCH" : 37,
# "MACIEJ PALUSZYŃSKI" : 65,
# "WITOLD PALUSZYŃSKI" : 38,
# "OLGIERD PANKIEWICZ" : 105,
# "JAKUB PETRYKOWSKI" : 95,
# "KRZYSZTOF PIECUCH" : 460,
# "BARBARA PIECZYRAK" : 489,
# "ZBIGNIEW PIETRZAK" : 106,
# "MAREK PIOTRÓW" : 39,
# "RAFAŁ PISZ" : 98,
# "ŁUKASZ PIWOWAR" : 40,
# "ZDZISŁAW PŁOSKI" : 41,
# "PIOTR POLESIUK" : 474,
# "IAN PRATT HARTMANN" : 103,
# "NIEZNANY PROWADZĄCY" : 119,
# "GABRIELA PRZESŁAWSKA" : 479,
# "STANISŁAW PRZYTOCKI" : 455,
# "PAWEŁ RAJBA" : 53,
# "MICHAŁ RÓŻAŃSKI" : 457,
# "EDYTA RUTKOWSKA-TOMASZEWSKA" : 505,
# "BARTOSZ RYBICKI" : 439,
# "PAWEŁ RYCHLIKOWSKI" : 42,
# "PAWEŁ RZECHONEK" : 43,
# "KATARZYNA SERAFIŃSKA" : 461,
# "PRZEMYSŁAW SKIBIŃSKI" : 100,
# "MARCIN SKÓRZEWSKI" : 75,
# "ANNA SMOLIŃSKA" : 452,
# "MACIEJ SOBCZAK" : 130,
# "PAWEŁ SOŁTYSIAK" : 91,
# "KRZYSZTOF SORNAT" : 459,
# "ZDZISŁAW SPŁAWSKI" : 3,
# "GRZEGORZ STACHOWIAK" : 44,
# "ŁUKASZ STAFINIAK" : 45,
# "PIOTR STANIOROWSKI" : 182,
# "ROBERT STAŃCZY" : 78,
# "DAMIAN STRASZAK" : 466,
# "MACIEJ SYSŁO" : 46,
# "MACIEJ M. SYSŁO" : 114,
# "ADMINISTRATOR SYSTEMU" : 451,
# "ANDRZEJ SZCZEPKOWICZ" : 502,
# "ZBIGNIEW SZCZUDŁO" : 179,
# "RAFAŁ SZUKIEWICZ" : 471,
# "RAFAŁ SZUKIEWICZ" : 492,
# "ADAM SZUSTALEWICZ" : 82,
# "MAREK SZYKUŁA" : 90,
# "KRZYSZTOF TABISZ" : 86,
# "KAMIL TABIŚ" : 56,
# "JAKUB TARNAWSKI" : 476,
# "BARTOSZ TROJAN" : 87,
# "TOMASZ TRUDERUNG" : 108,
# "ROMAN URBAN" : 4,
# "VACAT" : 192,
# "WIOLETTA WALDOWSKA" : 47,
# "RADOSŁAW WASIELEWSKI" : 122,
# "ROMAN WENCEL" : 88,
# "MONIKA WICHŁACZ" : 79,
# "PIOTR WIECZOREK" : 48,
# "TOMASZ WIERZBICKI" : 49,
# "PIOTR WIÓREK" : 454,
# "PIOTR WITKOWSKI" : 5,
# "MARCIN WŁODARCZAK" : 1,
# "PIOTR WNUK-LIPIŃSKI" : 176,
# "PIOTR WNUK-LIPIŃSKI" : 50,
# "MIECZYSŁAW WODECKI" : 51,
# "KATARZYNA WODZYŃSKA" : 128,
# "PAWEŁ WOŹNY" : 52,
# "MICHAŁ WRONA" : 80,
# "PAWEŁ ZALEWSKI" : 6,
# "JAN ZATOPIAŃSKI" : 126,
# "PAWEŁ ZAWIŚLAK" : 89,
# "ARTUR ZGODA" : 127,
# "KLARA ZIELIŃSKA" : 484,
# "TOMASZ ZIELIŃSKI" : 99,
# "GRAŻYNA ZWOŹNIAK" : 74,
# "WIKTOR ZYCHLA" : 7
# }




####  #####

import sys
import os
from django.core.management import setup_environ
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
        print("Not found: " + str(t))
        raise Exception("Teacher not found")
        return None

def get_classroom(rooms):
    classrooms = []
    for room in rooms:
        try:
            room = int(room)
            classroom = Classroom.objects.get(number=room)
        except ObjectDoesNotExist:
            print(bcolors.WARNING + room + ' <-wrong' + bcolors.ENDC)
            classroom = None
        except ValueError:
            print(bcolors.WARNING + room + ' <-wrong' + bcolors.ENDC)
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

def get_courses_ids(semester):
    cc = Course.objects.filter(semester=semester)
    for c in cc:
        print('"' + c.name.upper() + '" : '+ str(c.id) + ",")

def get_employers_ids():
    ee = Employee.objects.filter(status = 0)
    for e in ee:
        print('"' + e.get_full_name().upper() + '" : '+ str(e.id) + ",")        

def run():
    semester = get_semester()
    # get_courses_ids(semester)
    # get_employers_ids()
    print('Przenosimy na semestr <%s>' % semester)
    file = open(SCHEDULE_FILE)
    import_schedule(file, semester)

