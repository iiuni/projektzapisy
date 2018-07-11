from modeltranslation.translator import translator, TranslationOptions

from apps.enrollment.courses.models.course import CourseEntity, CourseDescription


class CourseEntityTranslationOptions(TranslationOptions):
    fields = ('name', )
    fallback_languages = {'default': ('pl',)}


translator.register(CourseEntity, CourseEntityTranslationOptions)


class CourseDescriptionTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(CourseDescription, CourseDescriptionTranslationOptions)
