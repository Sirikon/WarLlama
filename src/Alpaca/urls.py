from django.conf.urls import url

from . import views

app_name = "alpaca"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^activity/(?P<activity_id>[0-9]+)$', views.activity, name='activity'),
    url(r'^signup/(?P<activity_id>[0-9]*)$', views.signup, name='signup'),
    url(r'^login/(?P<activity_id>[0-9]*)$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout')
]