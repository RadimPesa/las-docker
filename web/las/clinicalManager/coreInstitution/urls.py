from django.conf.urls import patterns, include, url
from coreInstitution import views as vv
from coreInstitution.api import views

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'institution', views.InstitutionViewSet, 'institution')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = patterns('',
    url(r'^$', vv.index, name='index'),

    
    
    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

    #old Piston API
    #url(r'^apiPi/', include('appEnrollment.apiPi.urls')),

)

