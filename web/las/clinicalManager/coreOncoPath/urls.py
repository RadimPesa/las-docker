from django.conf.urls import patterns, include, url
from coreOncoPath import views as vv
from coreOncoPath.api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'oncoPath', views.OncoPathViewSet, 'oncoPath')
router.register(r'oncoPathDicts', views.OncoPathDictsViewSet, 'oncoPathDicts')




# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = patterns('',
    url(r'^$', vv.index, name='index'),



    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))


)
