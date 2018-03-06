
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from apps.users.models import Student, Program, UserProfile
import random
from sets import Set

IMPORT_FILE = 'importusos_17_18_zima.csv'
DEBUG = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def deactivate_all():
    print('deactivating all students...')
    students = Student.objects.all()
    for s in students:
        s.status = 1
        s.save()

def random_pass():
    alphabet = "abcdefghijkmnpqrstuvwxyz"
    upperalphabet = alphabet.upper()
    pw_len = 8
    pwlist = []

    for i in range(pw_len//3):
        pwlist.append(alphabet[random.randrange(len(alphabet))])
        pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
        pwlist.append(str(random.randrange(8)+2))
    for i in range(pw_len-len(pwlist)):
        pwlist.append(alphabet[random.randrange(len(alphabet))])

    random.shuffle(pwlist)
    pwstring = "".join(pwlist)

    return pwstring

def create_user(indeks, imie, nazwisko, mail):
    user = User.objects.create_user(username=indeks, email=mail, password=random_pass())
    user.first_name = imie
    user.last_name = nazwisko
    user.save()
    s = Student.objects.create(user=user, matricula=indeks)
    s.semestr = 1
    s.program = Program.objects.get(id=4)
    s.save()
    up = UserProfile.objects.create(user = user, is_student = True)
    return s

programs = set([])

def import_ects(file):
    for line in file:
        process(line)
    print('Używane programy:')
    print(programs)

def process(line):
    line = line.strip()
    indeks,imie,nazwisko,email,bk_email,ects,program,etap,aisdL,numerycznaL,dyskretnaL = line.split('|')
    
    if indeks == 'indeks':
        return
    
    ects = int(ects)
    programs.add(program)
    try:
        student = Student.objects.get(matricula=indeks)
    except ObjectDoesNotExist:
        print((bcolors.FAIL + "***" + str(indeks) + ". Brak studenta o tym indeksie. ECTS: " + str(ects) + bcolors.ENDC))
        if not DEBUG:
            student = create_user(indeks, imie, nazwisko, email)
        else:
            return

    student.status = 0
    student.isim = False

    if program == 'INF-K-S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia')
    elif program == 'ISIM-K-S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia')
        student.isim = True
    elif program == 'INF-K-2S1':
        student.program = Program.objects.get(name='Informatyka, dzienne I stopnia inżynierskie')
    elif program == 'INF-K-S2':
        student.program = Program.objects.get(name='Informatyka, dzienne II stopnia')
    elif program == 'INF-K-1S2':
        student.program = Program.objects.get(name='Informatyka, dzienne II stopnia inżynierskie')
    else:
        print((bcolors.FAIL + "***" + str(indeks) + ". Brak programu: " + program + bcolors.ENDC))
        return

    student.semestr = int(etap[-1])
    

    aisdL = int(aisdL)
    numerycznaL = int(numerycznaL)
    dyskretnaL = int(dyskretnaL)

    if aisdL > 0:
        student.algorytmy_l = True
    if numerycznaL > 0:
        student.numeryczna_l = True
    if dyskretnaL > 0:
        student.dyskretna_l = True


    if student.ects > ects:
        print((bcolors.WARNING))
    print((str((student, student.ects, ects, student.semestr)) + bcolors.ENDC))
    student.ects = ects
    if not DEBUG:
        student.save()


def run():
    if not DEBUG:
        deactivate_all()
    file = open(IMPORT_FILE)
    import_ects(file)