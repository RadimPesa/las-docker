from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^submitExperimentResult/$', 'api.funnel_api.submitExperimentResult'),

)
