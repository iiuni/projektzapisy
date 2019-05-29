from django.db import models

from apps.users.models import Employee, \
    Program
from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES

from .section import SectionOrdering, Section


class Template(models.Model):
    title = models.CharField(max_length=40, verbose_name='tytuł')
    description = models.TextField(blank=True, verbose_name='opis')
    studies_type = models.ForeignKey(
        Program,
        verbose_name='typ studiów',
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    no_course = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name='nie przypisany')
    deleted = models.BooleanField(blank=False, null=False, default=False, verbose_name='usunięty')
    exam = models.BooleanField(blank=False, null=False, default=True,
                               verbose_name='przedmiot z egzaminem')
    group_type = models.CharField(
        blank=True,
        null=True,
        max_length=2,
        choices=GROUP_TYPE_CHOICES,
        verbose_name='typ zajęć')
    sections = models.ManyToManyField(Section, verbose_name='sekcje',
                                      through='TemplateSections')

    in_grade = models.BooleanField(default=False, verbose_name='Szablon wykorzystywany w ocenie')

    author = models.ForeignKey(Employee, verbose_name='autor', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'szablon'
        verbose_name_plural = 'szablony'
        app_label = 'poll'
        ordering = ['title']

    def __str__(self):
        res = str(self.title)
        if self.studies_type:
            res += ', typ studiów: ' + str(self.studies_type)
        if self.course:
            res += ', przedmiot: ' + str(self.course)
        if self.group_type:
            res += ', typ grupy: ' + str(self.get_group_type_display())
        return res

    def all_sections(self):
        sections = self.templatesections_set.all().values_list('pk', flat=True)
        return Section.objects.filter(pk__in=sections)


class TemplateSections(models.Model):
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(Template, verbose_name='ankieta', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, verbose_name='sekcja', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'pozycje sekcji'
        verbose_name = 'pozycja sekcji'
        app_label = 'poll'
        ordering = ['id']

    def all_questions(self):
        return self.section.all_questions()
