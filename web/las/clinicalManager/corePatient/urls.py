from django.conf.urls import patterns, include, url
from corePatient import views as vv
from corePatient.api import views, patient_classic_rest
from django.conf import settings

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'patient', views.PatientViewSet, 'patient')
router.register(r'patient_classic_rest', patient_classic_rest.PatientViewSet, 'patient_classic_rest')
router.register(r'patient_for_client', views.PatientMergingViewSet, 'patient_for_client')






# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = patterns('',
    url(r'^crf$', vv.crf, name='crf'),
    url(r'^enrollment$', vv.enrollment, name='enrollment'),
    url(r'^list$', vv.enrollmentList, name='enrollmentList'),
    #url(r'^patientHome/', vv.PatientHome, name='PatientHome'),



    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))

    #old Piston API
    #url(r'^apiPi/', include('appEnrollment.apiPi.urls')),

)
