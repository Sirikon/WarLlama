from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import *

# ----- USER OVERRIDING ------
# Define an inline admin descriptor for Profile models
# which acts a bit like a singleton
class ProfileInLine(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInLine]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# ----------------------------

class SessionInline(admin.TabularInline):
    model = Session
    extra = 1

class ActivityAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Activity Description',{'fields': ['pub_date', 'author', 'title', 'description','attendants']}),
        ('Overall Settings',    {'fields': ['auto_register', 'confirmation_period', 'age_minimum']})
    ]
    inlines = [SessionInline]

class GroupAdmin(admin.ModelAdmin):
    model = Group
    fieldsets = [
        ('Group Description',   {'fields': ['logo', 'name', 'description', 'email']}),
        ('Members',             {'fields': ['superuser', 'admin_list', 'member_list']}),
        ('Requests',            {'fields': ['pending_members', 'pending_activities']}),
        ('Overall Settings',    {'fields': ['show_email', 'auto_register_users', 'auto_register_activities']})
    ]

class EventAdmin(admin.ModelAdmin):
    model = Event
    fieldsets = [
        ('Event Description',   {'fields': ['pub_date', 'group', 'cover', 'banner', 'title', 'description']}),
        ('Data',                {'fields': ['city', 'start_date', 'end_date', 'age_minimum']}),
        ('Attendants',          {'fields': ['attendants']}),
        ('Requests',            {'fields': ['pending_attendants']}),
        ('Settings',            {'fields': ['show_title', 'group_only_attendants', 'auto_register_users', 'auto_register_activities']})
    ]


admin.site.register(Activity, ActivityAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Event, EventAdmin)

