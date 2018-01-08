from django.conf.urls import url
from . import views

urlpatterns = [
    # records
    url('^set-enrolled(?P<method>\.json)?$',
        views.set_enrolled, name='records-set-enrolled'),
    url('^set-queue-priority(?P<method>\.json)?$',
        views.set_queue_priority, name='records-set-queue-priority'),
    url('^(?P<group_id>[\d]+)/records$',
        views.records, name='records-group'),
    url('^(?P<group_id>[\d]+)/records/group/csv$',
        views.records_group_csv, name='group-csv'),
    url('^(?P<group_id>[\d]+)/records/group/pdf$',
        views.records_group_pdf, name='group-pdf'),
    url('^(?P<group_id>[\d]+)/records/queue/csv$',
        views.records_queue_csv, name='queue-csv'),
    url('^(?P<group_id>[\d]+)/records/queue/pdf$',
        views.records_queue_pdf, name='queue-pdf'), 
    url('^set-locked(?P<method>\.json)?$',
        views.records_set_locked, name='records-set-locked'),

    # schedule and schedule prototype
    url('^schedule/$',
        views.own, name='schedule-own'),
    url('^schedule/prototype/$',
        views.schedule_prototype, name='schedule-prototype'),
    url('^schedule/prototype/set-pinned$',
        views.prototype_set_pinned, name='schedule-prototype-set-pinned'),
]
