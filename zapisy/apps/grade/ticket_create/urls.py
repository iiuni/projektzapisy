# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # feature do dodania w przyszłości
    url(r'^ajax_keys_progress$', 'apps.grade.ticket_create.views.ajax_keys_progress', name='grade-ticket-keys-progress'),
    url(r'^ajax_keys_generate$', 'apps.grade.ticket_create.views.ajax_keys_generate', name='grade-ticket-keys-generator'),
    url(r'^client_connection$',  'apps.grade.ticket_create.views.client_connection',  name='grade-ticket-client-connection'),
    url(r'^ajax_tickets1$',       'apps.grade.ticket_create.views.ajax_get_rsa_keys_step1',        name='grade-ticket-ajax-ticets1'),
    url(r'^ajax_tickets2$',       'apps.grade.ticket_create.views.ajax_get_rsa_keys_step2',        name='grade-ticket-ajax-ticets2'),
    url(r'^keys_list$',          'apps.grade.ticket_create.views.keys_list',           name='grade-ticket-keys-list'),
    url(r'^keys_generate$',      'apps.grade.ticket_create.views.keys_generate',           name='grade-ticket-keys-generate'),



    # feature do poprawienia w przyszłości
    url(r'^connections_choice$', 'apps.grade.ticket_create.views.connections_choice', name='grade-ticket-connections-choice')
)
