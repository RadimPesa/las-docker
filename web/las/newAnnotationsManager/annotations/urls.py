from django.conf.urls import patterns, include, url
from django.conf import settings


urlpatterns = patterns('',
    (r'^$', 'annotations.views.home'),
    (r'^home/$', 'annotations.views.home'),
    (r'^logout/$', 'annotations.views.logout_view'),

    (r'^funnelapi/', include('api.funnel_urls')),
    (r'^newapi/', include('api.newapi_urls')),

    (r'^create_targetseq/$', 'annotations.views.create_targetseq'),
    (r'^displayAlignReport/$', 'annotations.views.displayAlignReport'),
    (r'^create_seqpair/$', 'annotations.views.create_seqpair'),
    #(r'^pgdxEvaluate/$', 'annotations.views.pgdxEvaluate'),
    (r'^newFeatureValue/$', 'annotations.views.new_annotation_feature_value'),
    #(r'^reportAnnotations/$', 'annotations.views.report_annotations'),
    (r'^queryAnnotations/$', 'annotations.views.queryAnnotations'),
    (r'^getSAResults/$', 'annotations.views.getSAResults'),
    #(r'^plotGene/$', 'annotations.views.plotGene'),
    (r'^newMutation/$', 'annotations.views.newMutation'),
    (r'^newSGV/$', 'annotations.views.newSGV'),    
    (r'^newCNV/$', 'annotations.views.newCNV'),        
    (r'^defineTechnologies/$', 'annotations.views.defineAmpliconTechnologies'),
    (r'^sequenomReport/$', 'annotations.views.sequenomReport'),
    (r'^exploreKB/$', 'annotations.views.exploreKB'),
    (r'^fingerPrinting/$', 'annotations.views.fingerPrinting'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',  
         {'document_root':     settings.MEDIA_ROOT}),
    )



