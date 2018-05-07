#!/usr/bin/python

from apps.enrollment.courses.models import CourseEntity
import csv
import unicodedata

affected = 0
wrong = 0
with open('../przedmioty.csv') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        try:
            c = CourseEntity.objects.get(usos_kod=row[1])
            if unicodedata.normalize(
                'NFKD',
                c.name).replace(
                'ł',
                'l').encode(
                'ascii',
                    'ignore') != row[0]:
                wrong += 1
                print(';'.join(row))
            else:
                #c.usos_kod = row[2]
                # c.save()
                affected += 1
        except CourseEntity.DoesNotExist:
            print(';'.join(row))
            wrong += 1
print('Done. Wrong: ' + str(wrong) + '. Affected: ' + str(affected))
