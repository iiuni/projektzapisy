from django.urls import path

from . import views

urlpatterns = [
    path('', views.TicketsEntry.as_view(), name='grade-poll-main'),
    path('enter/', views.TicketsEntry.as_view(), name='grade-poll-tickets-enter'),
    path('submissions/', views.SubmissionEntry.as_view(), {'submission_index': 0}, name='grade-poll-submissions'),
    path('submissions/<int:submission_index>/', views.SubmissionEntry.as_view(), name='grade-poll-submissions'),
    path('results/', views.PollResults.as_view(), name='grade-poll-results'),
    path('results/semester/<int:semester_id>/', views.PollResults.as_view(), name='grade-poll-results'),
    path('results/semester/<int:semester_id>/poll/<int:poll_id>/', views.PollResults.as_view(), name='grade-poll-results'),
    path('results/semester/<int:semester_id>/poll/<int:poll_id>/submission/<int:submission_id>/', views.PollResults.as_view(), name='grade-poll-results'),
    path('clear/', views.ClearSession.as_view(), name='grade-poll-clear-session'),
]
