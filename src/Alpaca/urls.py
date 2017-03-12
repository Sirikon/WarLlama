from django.conf.urls import url

import views

app_name = "alpaca"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/group/$', views.group_index, name='group_index'),
    url(r'^index/event/$', views.event_index, name='event_index'),
    url(r'^about_us/$', views.about_us, name='about_us'),
    url(r'^terms_conditions/$', views.terms_conditions, name='terms_conditions'),

    url(r'^forgotpassword/$', views.forgot_password, name="forgot_password"),
    url(r'^resetpassword$', views.reset_password, name='reset_password'),

    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate$', views.activate, name='activate'),

    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    url(r'^profile/(?P<username>\w+)$', views.profile, name='profile'),
    url(r'^editprofile$', views.edit_profile, name='edit_profile'),
    url(r'^changepassword/$', views.change_password, name="change_password"),

    url(r'^group/new/$', views.new_group, name='new_group'),
    url(r'^group/(?P<group_id>[0-9]+)$', views.group, name='group'),
    url(r'^group/(?P<group_id>[0-9]+)/edit/$', views.edit_group, name='edit_group'),
    url(r'^group/join/(?P<group_id>[0-9]+)$', views.join_group, name='join_group'),
    url(r'^group/leave/(?P<group_id>[0-9]+)$', views.leave_group, name='leave_group'),
    url(r'^group/action/(?P<group_id>[0-9]+)$', views.handle_member, name='handle_member'),
    url(r'^group/demote/(?P<group_id>[0-9]+)$', views.demote_admin, name='demote_admin'),
    url(r'^group/members/(?P<group_id>[0-9]+)$', views.group_pending_members, name='group_pending_members'),
    url(r'^group/activities/(?P<group_id>[0-9]+)$', views.group_pending_activities, name='group_pending_activities'),

    url(r'^activity/new/$', views.new_activity, name='new_activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)$', views.activity, name='activity'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/$', views.edit_activity, name='edit_activity'),
    url(r'^activity/join/(?P<activity_id>[0-9]+)$', views.join_activity, name='join_activity'),
    url(r'^activity/leave/(?P<activity_id>[0-9]+)$', views.leave_activity, name='leave_activity'),
    url(r'^activity/kick/(?P<activity_id>[0-9]+)$', views.activity_kick_attendant, name='activity_kick_attendant'),
    url(r'^activity/pending/(?P<activity_id>[0-9]+)$', views.activity_pending_requests, name='activity_pending_attendants'),

    url(r'^activity/(?P<activity_id>[0-9]+)/new/$', views.new_session, name='new_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/edit/(?P<session_id>[0-9]+)$', views.edit_session, name='edit_session'),
    url(r'^activity/(?P<activity_id>[0-9]+)/confirm/$', views.confirm_session, name='confirm_session'),

    url(r'^event/new/(?P<group_id>[0-9]+)$', views.new_event, name='new_event'),
    url(r'^event/(?P<event_id>[0-9]+)$', views.event, name='event'),
    url(r'^event/(?P<event_id>[0-9]+)/edit/$', views.edit_event, name='edit_event'),
    url(r'^event/join/(?P<event_id>[0-9]+)$', views.join_event, name='join_event'),
    url(r'^event/leave/(?P<event_id>[0-9]+)$', views.leave_event, name='leave_event'),
    url(r'^event/kick/(?P<event_id>[0-9]+)$', views.event_kick_attendant, name='event_kick_attendant'),
    url(r'^event/attendants/(?P<event_id>[0-9]+)$', views.event_pending_attendants, name='event_pending_attendants'),
    url(r'^event/activities/(?P<event_id>[0-9]+)$', views.event_pending_activities, name='event_pending_activities'),
    url(r'^event/(?P<event_id>[0-9]+)/activity/new/$', views.event_new_activity, name='event_new_activity'),
]