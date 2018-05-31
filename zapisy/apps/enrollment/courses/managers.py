from django.db import models


class SimpleManager(models.Manager):

    def get_by_slug(self, slug):
        return self.get(slug=slug)

    def get_by_id(self, id):
        return self.get(id=id)


class FullManager(SimpleManager):

    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(FullManager, self).get_queryset().select_related('information')
