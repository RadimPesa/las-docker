from django.conf.urls.defaults import *



urlpatterns = patterns('',
    (r'^collection/$','mercuric.views.collectionMerc'),
    (r'^collection/save/$','mercuric.views.collectionSaveMerc'),
)
