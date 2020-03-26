from django.urls import path
from . import views

urlpatterns = [
    path('', views.plan_view, name='plan-view'),
    path('create/', views.plan_create, name='plan-create'),
    path('create/vote', views.plan_vote, name='plan-vote'),
    # create voting results sheet
    path('create/sheet', views.plan_create_voting_sheet,
         name='plan-create-voting-sheet'),
    # generate scheduler file
    path('create/scheduler/<slug:slug>/json', views.generate_scheduler_file_json,
         name='generate-scheduler-file-json'),
    path('create/scheduler/<slug:slug>/csv', views.generate_scheduler_file_csv,
         name='generate-scheduler-file-csv'),
]
