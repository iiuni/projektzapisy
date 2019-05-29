from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajax_get_courses$', views.ajax_get_courses, name='grade-poll-get-courses'),
    url(r'^ajax_get_groups$', views.ajax_get_groups, name='grade-poll-get-groups'),

    url(r'^tickets_enter$', views.tickets_enter, name='grade-poll-tickets-enter'),
    url(r'^polls/(?P<slug>[\w\-_]+)$', views.polls_for_user, name='grade-poll-polls-for-user'),

    url(r'^poll_answer/(?P<slug>[\w\-_]+)/(?P<pid>[0-9]+)/$', views.poll_answer, name='grade-poll-poll-answer'),
    url(r'^end_grading/$', views.poll_end_grading, name='poll-end-grading'),

    url(r'^semester/change$', views.change_semester, name='poll-change-semester'),

    url(r'^(?P<semester>[\d]*)/poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', views.poll_results, name='grade-poll-poll-results-semester'),
    url(r'^poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)?$', views.poll_results, name='grade-poll-poll-results'),

    url(r'^poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)/details/(?P<st_id>[1-9][0-9]*)?$', views.poll_results_detailed, name='grade-poll-poll-results-detailed'),
    url(r'^(?P<semester>[\d]*)/poll_results/(?P<mode>[S,T])(?P<poll_id>[1-9][0-9]*)/details/(?P<st_id>[1-9][0-9]*)?$', views.poll_results_detailed, name='grade-poll-poll-results-detailed-semester'),

    url(r'^managment/sections_list/$', views.sections_list, name='grade-poll-sections-list'),
    url(r'^managment/groups_without_polls/$', views.groups_without_poll, name='grade-poll-groups_without_polls'),
    url(r'^managment/poll_create/$', views.poll_create, name='grade-poll-poll-create'),
    url(r'^managment/poll/edit/form/(?P<poll_id>[1-9][0-9]*)/$', views.poll_edit_form, name='grade-poll-poll-edit-form'),
    url(r'^managment/poll/edit/$', views.poll_edit, name='grade-poll-poll-edit'),
    url(r'^managment/poll/form/$', views.poll_form, name='grade-poll-poll_form'),
    url(r'^managment/poll_create/(?P<group_id>[1-9][0-9]*)/$', views.poll_form, name='grade-poll-poll-create-group'),
    url(r'^managment/section/create/$', views.questionset_create, name='grade-poll-questionset-create'),
    url(r'^managment/section/form/$', views.get_section_form, name='grade-poll-get_section_form'),
    url(r'^managment/show_section/(?P<section_id>[1-9][0-9]*)/$', views.show_section, name='grade-poll-show_section'),
    url(r'^managment/section/action/$', views.section_actions, name='grade-poll-section_actions'),
    url(r'^managment/section/delete/$', views.delete_sections, name='grade-poll-delete_section'),
    url(r'^managment/show_poll/(?P<poll_id>[1-9][0-9]*)/$', views.show_poll, name='grade-poll-show_poll'),
    url(r'^managment/polls/action/$', views.poll_actions, name='grade-poll-poll_actions'),
    url(r'^managment/polls/delete/$', views.delete_polls, name='grade-poll-delete_poll'),
    url(r'^managment/templates/create/$', views.create_template, name='grade-poll-create-template'),
    url(r'^managment/templates/$', views.templates, name='grade-poll-templates'),
    url(r'^managment/templates/form/$', views.template_form, name='grade-poll-template_form'),
    url(r'^managment/templates/action/$', views.template_actions, name='grade-poll-template-action'),
    url(r'^managment/templates/show/(?P<template_id>[1-9][0-9]*)/$', views.show_template, name='grade-poll-show_template'),
    url(r'^managment/templates/use/$', views.use_templates, name='grade-poll-use-template'),
    url(r'^managment/templates/delete/$', views.delete_templates, name='grade-poll-delete_template'),
    url(r'^managment/edit_section/(?P<section_id>[1-9][0-9]*)/$', views.edit_section, name='grade-poll-edit-section'),

    url(r'^autocomplete$', views.autocomplete, name='grade-poll-autocomplete'),

    url(r'^get_section/(?P<section_id>[1-9][0-9]*)/$', views.get_section, name='grade-poll-get-section'),
]
