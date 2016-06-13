#-*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('apps.enrollment.records.views',
    # records
    url('^set-enrolled(?P<method>\.json)?$',
        'set_enrolled', name='records-set-enrolled'),
    url('^set-queue-priority(?P<method>\.json)?$',
        'set_queue_priority', name='records-set-queue-priority'),
    url('^(?P<group_id>[\d]+)/records$',
        'records', name='records-group'),
    url('^(?P<group_id>[\d]+)/records/group/csv$',
        'records_group_csv', name='group-csv'),
    url('^(?P<group_id>[\d]+)/records/group/pdf$',
        'records_group_pdf', name='group-pdf'),
    url('^(?P<group_id>[\d]+)/records/queue/csv$',
        'records_queue_csv', name='queue-csv'),
    url('^(?P<group_id>[\d]+)/records/queue/pdf$',
        'records_queue_pdf', name='queue-pdf'), 
    url('^set-locked(?P<method>\.json)?$',
        'records_set_locked', name='records-set-locked' ),

    #schedule and schedule prototype
    url('^schedule/$',
        'own', name='schedule-own' ),
    url('^schedule/prototype/$',
        'schedule_prototype', name='schedule-prototype' ),
    url('^schedule/prototype/set-pinned$',
        'prototype_set_pinned', name='schedule-prototype-set-pinned' ),
#
#    url('schedule/ajax/(?P<semester>[\d]+)', 'ajax_get_schedule',
#        name='get-schedule'
#       ),
)
