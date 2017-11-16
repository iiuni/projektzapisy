from apps.enrollment.courses.models import Course, Semester, CourseEntity, Semester, CourseDescription
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

def run():
    sem = Semester.objects.get(id=338)
    file = open('lista.txt')
    ids = []
    for line in file:
        title = line.strip()
        try:
            ce = CourseEntity.objects.get(name_pl__iexact = title)
            print ce
            ids.append(ce.id)
        except ObjectDoesNotExist:
            print bcolors.FAIL+'   [not exists error] '+title+bcolors.ENDC
        except MultipleObjectsReturned:
            print bcolors.FAIL+'   [multiple objects error (took newest,for vote)] '+title+bcolors.ENDC
            ce = CourseEntity.objects.filter(name_pl__iexact = title,status=2).order_by('-id')[0]
            ids.append(ce.id)

    for idd in ids:
            ent = CourseEntity.objects.get(id=idd)
            if ent.slug is None:
                    print bcolors.FAIL+'   [slug error] '+ent.name+bcolors.ENDC
            else:
                    newslug = ent.slug+'_zima_17_18'
                    cour = Course(entity=ent, information=ent.information, semester=sem, slug=newslug)
                    cour.save()
                    print ent.name + ' $ ' + newslug + ' $ ' + str(cour.id)

