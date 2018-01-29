from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^collection/$','symphogen.views.collectionSym'),
    (r'^collection/save/$','symphogen.views.collectionSaveSym'),
)
