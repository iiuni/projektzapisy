from django.db import models


class TermSyncData(models.Model):
    """Stores the group numbers for the scheduler IDs so the importer can detect changes"""
    term = models.ForeignKey('courses.Term', on_delete=models.CASCADE, verbose_name='termin')
    scheduler_id = models.PositiveIntegerField(null=True,
                                               verbose_name='id grupy w schedulerze')

    class Meta:
        verbose_name = 'Obiekt synchronizacji terminów grup'
        verbose_name_plural = 'Obiekty synchronizacji terminów grup'
        app_label = 'schedulersync'


class EmployeeMap(models.Model):
    """Map employee name from scheduler API, can set to unknown employee"""
    scheduler_username = models.CharField(unique=True, max_length=150, blank=False)
    employee_username = models.CharField(default='Nn', max_length=150, blank=False)

    class Meta:
        verbose_name = "Mapa pracowników"
        verbose_name_plural = "Mapy pracowników"

    def __str__(self):
        return self.scheduler_username

class CourseMap(models.Model):
    """Map course name from scheduler API, can set to not import that course"""
    scheduler_course = models.CharField(unique=True, max_length=100, blank=False)
    course = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = "Mapa przedmiotów"
        verbose_name_plural = "Mapy przedmiotów"

    def __str__(self):
        return self.scheduler_course