from django.conf.urls.defaults import *
from archive.models import *
from storage import settings
from django.conf.urls.static import static

urlpatterns = patterns('archive.views',
    (r'^$', 'index'),
    (r'^full/$','TubeFull'),
    (r'^saveFFPE/$','SaveFF'),
    (r'^savetube/$','SaveTube'),
    (r'^cancFFPE/$','CancFF'),
    (r'^container/availability/$','ContainerAvailability'),
    (r'^container/type/','InsertContainerType'),
    (r'^container/insert/','InsertNewContainerInstance'),
    #(r'^container/final/','InsertNewContainerFinal'),
    (r'^container/batch/','InsertContainerBatch'),
    (r'^ajax/container/autocomplete/','AjaxContainerAutoComplete'),
    (r'^logout/$','logout'),
    (r'^login/$', 'login'),
    #(r'^plate/insert/$','InsertPlate'),
    (r'^plate/change/$','ChangePlate'),
    #(r'^plate/change/final/$','ChangePlateFinal'),
    (r'^store/$','storeAliquots'),
    (r'^store/save/$','saveStoreAliquots'),
    (r'^store/cassette/$','saveStoreAliquotsCassette'),
    (r'^move/$','MoveAliquots'),
    (r'^move/save/$','SaveMoveAliquots'),
    (r'^put/start/$','PutAwayAliquots'),
    (r'^put/last/$','PutAwayAliquotsLast'),
    
    (r'^archive/$','ArchiveContainer'),
    
    (r'^error/$','error'),
    
    (r'^create/plate/$','CreatePlate'),
    (r'^prova/plate/$','ProvaCreatePlate'),
    (r'^prova/aliq/$','ProvaAliquotHandler'),
    
    (r'^create/geometry/$','CreateGeometry'),
    (r'^copy/geom/$','CopyGeometry'),
    
    (r'^update/present/$','UpdatePresent'),
    (r'^set/full/$','SetFull'),
    (r'^hub/create/$','HubCreate'),
    
    (r'^query/$','Query'),
    
    (r'^historic/box$','HistoricBox'),
    (r'^historic/plate$','HistoricPlate'),
    (r'^historic/rack$','HistoricRack'),
    (r'^historic/beamingcontainer$','HistoricBeamingContainer'),
    
    (r'^historic/tube$','HistoricBoxTube'),
    (r'^historic/ffpe$','HistoricFFPETube'),
    
    (r'^create/aliquot$','CreateAliquot'),
    (r'^create/feature$','CreateFeature'),
    
    (r'^login/$', 'login'),
)

urlpatterns += patterns('',
    (r'^archive_media/(?P<path>.*)$', 'django.views.static.serve',  
     {'document_root':     settings.MEDIA_ROOT}),
)

