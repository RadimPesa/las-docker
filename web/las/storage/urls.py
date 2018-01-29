from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import *

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^$', 'archive.views.start_redirect'),
    (r'^', include('archive.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^api.', include('api.urls')),
    (r'^auth/', include('LASAuth.urls')),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^forbidden/', 'django.views.defaults.permission_denied'),
    (r'^permission/', include('editpermission.urls')),
    (r'^clientHUB/', include('clientHUB.urls')),
    (r'^mdamapi/', include('api.mdamurls')),
)
