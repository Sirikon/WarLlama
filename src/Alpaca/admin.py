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
        (None,          {'fields': ['pub_date', 'author', 'title', 'description']}),
        ('Settings',    {'fields': ['auto_register', 'confirmation_period', 'age_minimum']})
    ]
    inlines = [SessionInline]

admin.site.register(Activity, ActivityAdmin)

