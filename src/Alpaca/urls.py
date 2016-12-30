from django.conf.urls import url

import views

app_name = "alpaca"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^demo/$', views.index_demo, name='index_demo'),
    url(r'^about_us/$', views.about_us, name='about_us'),
    url(r'^terms_conditions/$', views.terms_conditions, name='terms_conditions'),

    url(r'^forgotpassword/$', views.forgot_password, name="forgot_password"),
    url(r'^resetpassword$', views.reset_password, name='reset_password'),

    url(r'^signup/(?P<activity_id>[0-9]*)$', views.signup, name='signup'),
    url(r'^activate$', views.activate, name='activate'),

    url(r'^login/(?P<activity_id>[0-9]*)$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    url(r'^profile/(?P<username>\w+)$', views.profile, name='profile'),
    url(r'^editprofile$', views.edit_profile, name='edit_profile'),
    url(r'^changepassword/$', views.change_password, name="change_password"),

    url(r'^groupindex/$', views.group_index, name='group_index'),
    url(r'^group/new/$', views.new_group, name='new_group'),
    url(r'^group/(?P<group_id>[0-9]+)$', views.group, name='group'),
    url(r'^group/(?P<group_id>[0-9]+)/edit/$', views.edit_group, name='edit_group'),
    url(r'^group/join/(?P<group_id>[0-9]+)$', views.join_group, name='join_group'),
    url(r'^group/leave/(?P<group_id>[0-9]+)$', views.leave_group, name='leave_group'),
    url(r'^group/members/(?P<group_id>[0-9]+)$', views.pending_members, name='pending_members'),
    url(r'^group/activities/(?P<group_id>[0-9]+)$', views.pending_activities, name='pending_activities'),
    url(r'^group/action/(?P<group_id>[0-9]+)$', views.handle_member, name='handle_member'),
    url(r'^group/demote/(?P<group_id>[0-9]+)$', views.demote_admin, name='demote_admin'),

    url(r'^activity/new/$', views.new_activity, name='new_activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)$', views.activity, name='activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/$', views.edit_activity, name='edit_activity'),
    url(r'^activity/join/(?P<activity_id>[0-9]+)$', views.join_activity, name='join_activity'),
    url(r'^activity/leave/(?P<activity_id>[0-9]+)$', views.leave_activity, name='leave_activity'),
    url(r'^activity/kick/(?P<activity_id>[0-9]+)$', views.kick_attendant, name='kick_attendant'),
    url(r'^activity/pending/(?P<activity_id>[0-9]+)$', views.pending_requests, name='pending_requests'),
    url(r'^activity/(?P<activity_id>[0-9]+)/new/$', views.new_session, name='new_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/(?P<session_id>[0-9]+)$', views.edit_session, name='edit_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/confirm/$', views.confirm_session, name='confirm_session'),

    url(r'^event/new/(?P<group_id>[0-9]+)$', views.new_event, name='new_event'),
    url(r'^event/(?P<event_id>[0-9]+)$', views.event, name='event'),
    url(r'^event/(?P<event_id>[0-9]+)/edit/$', views.edit_event, name='edit_event'),
    url(r'^event/join/(?P<event_id>[0-9]+)$', views.join_event, name='join_event'),
    url(r'^event/leave/(?P<event_id>[0-9]+)$', views.leave_event, name='leave_event'),
    url(r'^event/attendants/(?P<event_id>[0-9]+)$', views.pending_attendants, name='pending_attendants'),
    url(r'^event/activities/(?P<event_id>[0-9]+)$', views.pending_activities, name='pending_activities'),
    url(r'^event/kick/(?P<event_id>[0-9]+)$', views.kick_attendant, name='kick_attendant'),
]