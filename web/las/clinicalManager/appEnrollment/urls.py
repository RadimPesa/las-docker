"""
from django.conf.urls.defaults import *
from django.contrib.auth.views import *


urlpatterns = patterns('',
    url(r'^api/', include('appEnrollment.api.urls')),
)
"""

from django.conf.urls import patterns, include, url
from appEnrollment import views as vv
from appEnrollment.api import views

from rest_framework import routers


router = routers.DefaultRouter()
#router.register(r'test', views.PatientViewSet, 'test')
router.register(r'enrollment', views.EnrollmentViewSet, 'enrollment')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = patterns('',
    url(r'^$', vv.index, name='index'),

    
    
    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

    #old Piston API
    #url(r'^apiPi/', include('appEnrollment.apiPi.urls')),

)

