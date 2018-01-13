# -*- coding: utf-8 -*-

from django import template

register = template.Library()

from apps.news.models import News


@register.simple_tag
def newscount(category):
    """Wyświetla liczbę nowych ogłoszeń."""
    return(str(News.objects.count_new(category)))
