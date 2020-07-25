from django.urls import path

from . import views

urlpatterns = [
    path('', views.plan_view, name='plan-view'),
    path('create/', views.plan_creator, name='plan-creator'),
    path('create/assignments', views.create_assignments_sheet, name='create-assignments-sheet'),
    # create voting results sheet
    path('create/voting', views.create_voting_sheet, name='create-voting-sheet'),
    # generate scheduler file
    path('create/scheduler/<slug:semester>/<slug:fmt>',
         views.generate_scheduler_file,
         name='generate-scheduler-file'),
]
