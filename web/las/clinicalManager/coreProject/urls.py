from django.conf.urls import patterns, include, url
from coreProject import views as vv
from coreProject.api import views

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'informedConsent', views.IcViewSet, 'informedConsent')
router.register(r'project', views.ProjectViewSet, 'project')
router.register(r'localId', views.LocalIdViewSet, 'localId')
router.register(r'icBatch', views.IcBatchViewSet, 'icBatch')
router.register(r'enrollmentsList', views.EnrollmentsListViewSet, 'enrollmentsList')
router.register(r'patientListedByProject', views.PatientsByProject, 'patientListedByProject')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = patterns('',
    url(r'^$', vv.index, name='index'),



    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

    #old Piston API
    #url(r'^apiPi/', include('appEnrollment.apiPi.urls')),

)
