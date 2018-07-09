from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^keys_list$', views.keys_list, name='grade-ticket-keys-list'),
    url(r'^keys_generate$', views.keys_generate, name='grade-ticket-keys-generate'),
    url(r'^sign_tickets$', views.sign_tickets, name='grade-ticket-sign-tickets'),
    url(r'^get_tickets$', views.get_tickets, name='grade-ticket-get-tickets'),
    url(r'^ajax_tickets1$', views.ajax_get_rsa_keys_step1, name='grade-ticket-ajax-ticets1'),
    url(r'^ajax_tickets2$', views.ajax_get_rsa_keys_step2, name='grade-ticket-ajax-ticets2')
]
