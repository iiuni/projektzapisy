from mailer.models import Message
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student, Program, UserProfile
from django.contrib.auth.models import User
import random

studentsfile = 'newstudents2016.txt'

def create_user(indeks, imie, nazwisko, mail, isim, pswd):
    p = Program.objects.get(id=4)
    user = User.objects.create_user(username=indeks, email=mail, password=pswd)
    user.first_name = imie
    user.last_name = nazwisko
    user.save()
    s = Student.objects.create(user=user, matricula=indeks)
    s.isim = isim
    s.semestr = 1
    s.program = p
    s.save()
    up = UserProfile.objects.create(user = user, is_student = True)
    return user

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

def process(line):
    line = line.strip()
    indeks, imie, nazwisko, mail, program = line.split(',')
    try:
        student = Student.objects.get(matricula=indeks)
    except ObjectDoesNotExist:
        haslo = random_pass()
        isim = False
        if program == 'ISIM':
            isim = True
        create_user(indeks, imie, nazwisko, mail, isim, haslo)
        print(imie + ',' + nazwisko + ',' + indeks + ',' + haslo + ',' + program)
    else:
        print(str(indeks)+': already exists')


def run():
    file = open(studentsfile)
    for line in file:
        process(line)
