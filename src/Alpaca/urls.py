from django.conf.urls import url

from . import views

app_name = "alpaca"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^activity/(?P<activity_id>[0-9]+)$', views.activity, name='activity'),
]