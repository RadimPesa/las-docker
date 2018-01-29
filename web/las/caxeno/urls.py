from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import *

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^$', 'xenopatients.views.start_redirect'),
    (r'^', include('xenopatients.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^api.', include('api.urls')),
    (r'^auth/', include('LASAuth.urls')),
    (r'^mdamapi/', include('api.mdamurls')),
    (r'forbidden/', 'django.views.defaults.permission_denied'),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
)
