from django.urls import path

from . import views

urlpatterns = [
    path('', views.plan_view, name='assignments-view'),
    path('wizard/', views.assignments_wizard, name='assignments-wizard'),
    path('wizard/assignments', views.create_assignments_sheet, name='create-assignments-sheet'),
    # create voting results sheet
    path('wizard/voting', views.create_voting_sheet, name='create-voting-sheet'),
    # generate scheduler file
    path('wizard/scheduler/<slug:semester>/<slug:fmt>',
         views.generate_scheduler_file,
         name='generate-scheduler-file'),
]
