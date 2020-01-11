from django.urls import path
from . import views

urlpatterns = [
    path('', views.plan_view, name='plan-view'),
    path('create/', views.plan_create, name='plan-create'),
    path('create/vote', views.plan_vote, name='plan-vote'),
    # create voting results sheet
    path('create/sheet', views.plan_create_voting_sheet, name='plan-create-voting-sheet'),
    # generate plan html at /plan
    path('create/plan', views.generate_plan_html, name='generate-plan-html'),
]
