from django.conf.urls import patterns, url

urlpatterns = patterns('apps.grade.poll.views',

    url(r'^ajax_get_courses$',  'ajax_get_courses',  name='grade-poll-get-courses'),
    url(r'^ajax_get_groups$',    'ajax_get_groups',    name='grade-poll-get-groups'),

    url(r'^tickets_enter$', 'tickets_enter', name='grade-poll-tickets-enter'),
    url(r'^polls/(?P<slug>[\w\-_]+)$',         'polls_for_user', name='grade-poll-polls-for-user'),
    
    url(r'^poll_answer/(?P<slug>[\w\-_]+)/(?P<pid>[0-9]+)/$', 'poll_answer', name='grade-poll-poll-answer'),
    url(r'^end_grading/$', 'poll_end_grading', name='poll-end-grading'),

    url(r'^semester/change$', 'change_semester', name='poll-change-semester'),

    url(r'^(?P<semester>[\d]*)/poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', 'poll_results', name='grade-poll-poll-results-semester'),
    url(r'^poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', 'poll_results', name='grade-poll-poll-results'),

    url(r'^poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)/details/(?P<st_id>[1-9][0-9]*)?$', 'poll_results_detailed', name='grade-poll-poll-results-detailed'),
    url(r'^(?P<semester>[\d]*)/poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)/details/(?P<st_id>[1-9][0-9]*)?$', 'poll_results_detailed', name='grade-poll-poll-results-detailed-semester'),


    #url(r'^share_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', 'share_results_toggle', name='grade-poll-share-results'),
#    url(r'^save_csv/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', 'save_csv', name='grade-poll-save-csv'),
#
    url(r'^managment/polls_list/$', 'polls_list', name='grade-poll-list'),
    url(r'^managment/sections_list/$', 'sections_list', name='grade-poll-sections-list'),
    url(r'^managment/groups_without_polls/$', 'groups_without_poll', name='grade-poll-groups_without_polls'),
    url(r'^managment/poll_create/$', 'poll_create', name='grade-poll-poll-create'),
    url(r'^managment/poll/edit/form/(?P<poll_id>[1-9][0-9]*)/$', 'poll_edit_form', name='grade-poll-poll-edit-form'),
    url(r'^managment/poll/edit/$', 'poll_edit', name='grade-poll-poll-edit'),
    url(r'^managment/poll/form/$', 'poll_form', name='grade-poll-poll_form'),
    url(r'^managment/poll_create/(?P<group_id>[1-9][0-9]*)/$', 'poll_form', name='grade-poll-poll-create-group'),
    url(r'^managment/section/create/$', 'questionset_create', name='grade-poll-questionset-create'),
    url(r'^managment/section/form/$', 'get_section_form', name='grade-poll-get_section_form'),
    url(r'^managment/show_section/(?P<section_id>[1-9][0-9]*)/$', 'show_section', name='grade-poll-show_section'),
    url(r'^managment/section/action/$', 'section_actions', name='grade-poll-section_actions'),
    url(r'^managment/section/delete/$', 'delete_sections', name='grade-poll-delete_section'),
    url(r'^managment/show_poll/(?P<poll_id>[1-9][0-9]*)/$', 'show_poll', name='grade-poll-show_poll'),
    url(r'^managment/polls/action/$', 'poll_actions', name='grade-poll-poll_actions'),
    url(r'^managment/polls/delete/$', 'delete_polls', name='grade-poll-delete_poll'),
    url(r'^managment/templates/create/$', 'create_template', name='grade-poll-create-template'),
    url(r'^managment/templates/$', 'templates', name='grade-poll-templates'),
    url(r'^managment/templates/form/$', 'template_form', name='grade-poll-template_form'),
    url(r'^managment/templates/action/$', 'template_actions', name='grade-poll-template-action'),
    url(r'^managment/templates/show/(?P<template_id>[1-9][0-9]*)/$', 'show_template', name='grade-poll-show_template'),
    url(r'^managment/templates/use/$', 'use_templates', name='grade-poll-use-template'),
    url(r'^managment/templates/delete/$', 'delete_templates', name='grade-poll-delete_template'),
    url(r'^managment/edit_section/(?P<section_id>[1-9][0-9]*)/$', 'edit_section', name='grade-poll-edit-section'),
    
    
           
    url(r'^autocomplete$', 'autocomplete', name='grade-poll-autocomplete'),
    
    url(r'^get_section/(?P<section_id>[1-9][0-9]*)/$', 'get_section', name='grade-poll-get-section'),
)
