from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import *
admin.autodiscover()

urlpatterns = patterns('',
     #(r'^$', 'tissue.views.start_redirect'),
#     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
     (r'^admin/', include(admin.site.urls)),
     (r'^', include('tissue.urls')),
#     (r'^tissue/login/$', 'django.contrib.auth.views.login', {'template_name': 'tissue2/login.html'}),
     (r'^api/', include('api.urls')),
     (r'^auth/', include('LASAuth.urls')),
     (r'^forbidden/', 'django.views.defaults.permission_denied'),
     (r'^permission/', include('editpermission.urls')),
     (r'^clientHUB/', include('clientHUB.urls')),
     (r'^mdamapi/', include('api.mdamurls')),
     (r'^mercuric/', include('mercuric.urls')),
     (r'^funnel/', include('funnel.urls')),
     (r'^symphogen/', include('symphogen.urls')),
     (r'^motricolor/', include('motricolor.urls')),
)
