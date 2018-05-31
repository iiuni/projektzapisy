from apps.enrollment.courses.models.course import CourseEntity, CourseDescription


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
    for ce in CourseEntity.noremoved.all():
        descs = CourseDescription.objects.filter(entity=ce).order_by('-id')
        if len(descs) == 0:
            print(bcolors.FAIL + '   [no description] ' + ce.name_pl + bcolors.ENDC)
        else:
            if ce.information == descs[0]:
                print(bcolors.OKGREEN + ce.name_pl + bcolors.ENDC)
            else:
                print(bcolors.WARNING + ce.name_pl + bcolors.ENDC)
                print(str(descs[0]) + ' || ' + str(ce.information))
                ce.information = descs[0]
                ce.save()
