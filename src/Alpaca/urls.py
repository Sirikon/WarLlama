from django.conf.urls import url

import views

app_name = "alpaca"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/(?P<activity_id>[0-9]*)$', views.signup, name='signup'),
    url(r'^login/(?P<activity_id>[0-9]*)$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^resetpassword/$', views.reset_password, name="reset_password"),
    url(r'^newactivity/$', views.new_activity, name='new_activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)$', views.activity, name='activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/$', views.edit_activity, name='edit_activity'),
    url(r'^activity/join/(?P<activity_id>[0-9]+)$', views.join_activity, name='join_activity'),
    url(r'^activity/leave/(?P<activity_id>[0-9]+)$', views.leave_activity, name='leave_activity'),
    url(r'^activity/kick/(?P<activity_id>[0-9]+)$', views.kick_attendant, name='kick_attendant'),
    url(r'^activity/pending/(?P<activity_id>[0-9]+)$', views.pending_requests, name='pending_requests'),
    url(r'^activity/(?P<activity_id>[0-9]+)/new/$', views.new_session, name='new_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/(?P<session_id>[0-9]+)$', views.edit_session, name='edit_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/confirm/$', views.confirm_session, name='confirm_session'),
]