from django.urls import include, path

urlpatterns = [
    path('assignments/', include('apps.offer.assignments.urls')),
    path('desiderata/', include('apps.offer.desiderata.urls')),
    path('preferences/', include('apps.offer.preferences.urls')),
    path('vote/', include('apps.offer.vote.urls')),
    path('', include('apps.offer.proposal.urls')),
]
