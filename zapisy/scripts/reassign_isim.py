
from django.core.exceptions import ObjectDoesNotExist
from zapisy.apps.users.models import Student

filename = 'isim.txt'

def process(line):
    indeks = line.strip()
    s = None
    try:
        s = Student.objects.get(matricula=indeks)
    except ObjectDoesNotExist:
        print(("***" + indeks + ": brak"))
        return
    s.isim = True
    s.save()

def remove_all_isim():
    ss = Student.objects.filter(isim=True)
    for s in ss:
        s.isim = False
        s.save()
    print(("old isim students count: "+str(len(ss))))

def run():
    remove_all_isim()
    file = open(filename)
    c = 0
    for line in file:
        process(line)
        c += 1
    print(("new isim students count: "+str(c)))