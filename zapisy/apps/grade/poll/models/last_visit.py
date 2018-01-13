# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from apps.grade.poll.models.poll import Poll


class LastVisit(models.Model):
    user = models.ForeignKey(User)
    poll = models.ForeignKey(Poll)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'ogladane'
        verbose_name = 'ogladane'
        app_label = 'poll'

        unique_together = ('user', 'poll')
