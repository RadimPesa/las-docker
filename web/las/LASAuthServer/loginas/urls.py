from django.conf.urls import url
from loginas.views import user_logout, other_login

urlpatterns = [
    url(r"^logout/$", user_logout, name="loginas-logout"),
    url(r"^loginasuser/$", other_login, name="loginas-login"),
]
