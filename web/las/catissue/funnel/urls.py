from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^collection/$','funnel.views.collectionFunnel'),
    (r'^collection/save/$','funnel.views.collectionSaveFunnel'),
)
