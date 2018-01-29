from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^collection/motr1$','motricolor.views.collectionMotr1'),
    (r'^collection/motr2$','motricolor.views.collectionMotr2'),
    (r'^collection/motr3$','motricolor.views.collectionMotr3'),
    (r'^collection/save/$','motricolor.views.collectionSaveMotr'),
)
