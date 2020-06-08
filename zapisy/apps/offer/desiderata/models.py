from django.db import models

from apps.common import days_of_week


class Desiderata(models.Model):
    employee = models.ForeignKey(
        'users.Employee',
        verbose_name='prowadzący',
        on_delete=models.CASCADE)
    day = models.CharField(max_length=1, choices=days_of_week.DAYS_OF_WEEK, verbose_name='dzień tygodnia')
    hour = models.IntegerField(verbose_name='godzina')

    @staticmethod
    def get_desiderata(employee):
        desideratas = Desiderata.objects.filter(employee=employee)
        result = {}
        for day in range(1, 8, 1):
            result[str(day)] = {}
            for hour in range(8, 22, 1):
                result[str(day)][hour] = None
        for desiderata in desideratas:
            result[desiderata.day][desiderata.hour] = desiderata
        return result

    @staticmethod
    def get_desiderata_to_formset(desideratas):
        result = []
        result_append = result.append
        for day in desideratas:
            for hour in desideratas[day]:
                value = not bool(desideratas[day][hour])
                result_append({'day': day, 'hour': hour, 'value': value})
        return result


class DesiderataOther(models.Model):
    employee = models.OneToOneField(
        'users.Employee', verbose_name='prowadzący', on_delete=models.CASCADE)
    comment = models.TextField("inne uwagi", max_length=1000, blank=True)
