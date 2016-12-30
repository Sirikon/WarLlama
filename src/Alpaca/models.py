# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .storage import *
from file_paths import *

import datetime
import re #RegEx
    
## -- USERS -- ##
class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField( upload_to=user_avatar_path, 
                                storage=OverwriteStorage(),
                                null=True, blank=True,
                                default="no-avatar.png")

    birth_date = models.DateField('date of birth')

    current_token = models.CharField(max_length=100, default="")

    # USER SETTINGS #
    language_preference = models.CharField(max_length=50, default="English")
    show_email = models.BooleanField(default=True)
    show_birthday = models.BooleanField(default=True)
    show_real_name = models.BooleanField(default=True)
    display_name_format = models.CharField(max_length=50, default="nick (full_name)")

    def __str__(self):
        return self.user.username

    def get_full_name(self):
        full_name = ""
        if self.user.first_name != "":
            full_name = self.user.first_name
            if self.user.last_name != "":
                full_name += " " + self.user.last_name

        elif self.user.last_name != "":
            full_name = self.user.last_name

        return full_name            

    def get_display_name(self):
        if self.show_real_name and (self.user.first_name != "" or self.user.last_name != ""):
            display_name = self.display_name_format.replace("nick", self.user.username)
            display_name = display_name.replace("full_name", self.get_full_name())
            display_name = display_name.replace("first_name", self.user.first_name)
            display_name = display_name.replace("last_name", self.user.last_name)
            display_name = display_name.replace("()", "")
            return display_name
        return self.user.username

class Group (models.Model):
    logo = models.ImageField( upload_to=group_logo_path, 
                                storage=OverwriteStorage(),
                                null=True, blank=True,
                                default="no-logo.png")
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    email = models.EmailField(max_length=254)

    superuser = models.OneToOneField(User)
    admin_list = models.ManyToManyField(User, related_name="admin_of", blank=True)
    member_list = models.ManyToManyField(User, related_name="member_of", blank=True)
    total_num_members = models.IntegerField(default=0)

    pending_members = models.ManyToManyField(User, related_name="waiting_groups", blank=True)

    creation_date = models.DateTimeField('creation date')

    # Settings
    show_email = models.BooleanField(default=True)
    auto_register_users = models.BooleanField(default=False)
    auto_register_activities = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " - #" + str(1 + self.admin_list.count() + self.member_list.count())

    def member_count(self):
        return  1 + self.admin_list.count() + self.member_list.count()

    def get_short_description(self):
        temp = re.sub("(<img)(?<=(<img)).*?(?=>)(>)", " ", self.description)

        if len(temp) > 200:
            temp = temp[:200]
            
        return temp


## -- ACTIVITIES -- ##
class Activity (models.Model):
    cover = models.ImageField( upload_to=activity_cover_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=activity_no_cover_path )


    title = models.CharField(max_length=200)
    description = models.TextField(max_length=5000)
    city = models.TextField(max_length=100)
    pub_date = models.DateTimeField('publication date')
   
    group = models.ForeignKey(Group, related_name="activity_list", blank=True, null=True)
    pending_group = models.ForeignKey(Group, related_name="pending_activities", blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_activities")
    attendants = models.ManyToManyField(User, related_name="attending_activities", blank=True)
    num_attendants = models.IntegerField(default=0)
    pending_attendants = models.ManyToManyField(User, related_name="waiting_activities", blank=True)

    # Settings
    auto_register = models.BooleanField(default=False)
    confirmation_period = models.IntegerField(default=3, validators=[MinValueValidator(3)])
    age_minimum = models.IntegerField(default=0)

    def __str__(self):
        return self.pub_date.strftime('(%Y-%m-%d, %H:%M)') + " " + self.title + " - Author: " + self.author.username

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.title, d=self.description)

    def get_past_sessions(self):
        today = timezone.now()
        return self.session_set.filter(Q(start_date__lt=today))
        
    def get_future_sessions(self):
        today = timezone.now()
        return self.session_set.filter(Q(start_date__gt=today))

    def get_next_session(self):
        return self.get_future_sessions().order_by('start_date').first()

    def is_user_old_enough(self, user):
        # http://stackoverflow.com/questions/2217488/age-from-birthdate-in-python/9754466#9754466
        today = timezone.now()
        born = user.profile.birth_date
        years_difference = today.year - born.year
        is_before_birthday = (today.month, today.day) < (born.month, born.day)
        elapsed_years = years_difference - int(is_before_birthday)
        return elapsed_years >= self.age_minimum

    def get_short_description(self):
        temp = re.sub("(<img)(?<=(<img)).*?(?=>)(>)", " ", self.description)

        if len(temp) > 200:
            temp = temp[:200]
            
        return temp

class Event (models.Model): 
    cover = models.ImageField( upload_to=activity_cover_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=activity_no_cover_path )

    banner = models.ImageField( upload_to=activity_cover_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=activity_no_cover_path )

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=5000)
    city = models.TextField(max_length=100)
    pub_date = models.DateTimeField('publication date')
   
    author_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="owned_events")
    organizers = models.ManyToManyField(User, related_name="organizing_events", blank=True)
    attendants = models.ManyToManyField(User, related_name="attending_events", blank=True)
    num_attendants = models.IntegerField(default=0)

    pending_attendants = models.ManyToManyField(User, related_name="waiting_events", blank=True)
    pending_activities = models.ManyToManyField(Activity, blank=True)

    # Settings
    group_only_attendants = models.BooleanField(default=False)
    allow_any_users = models.BooleanField(default=True) 
    auto_register_users = models.BooleanField(default=True)
    auto_register_activities = models.BooleanField(default=False)    
    age_minimum = models.IntegerField(default=0)


class Session (models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)

    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

    location = models.CharField(max_length=100)
    confirmed_attendants = models.ManyToManyField(User, blank=True)
    emails_are_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.description + " - " + self.start_date.strftime('%Y-%m-%d, from %H:%M') + " " + self.end_date.strftime('to %Y-%m-%d, %H:%M') 

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.activity.title, d=self.description)

    def has_finished(self):
        now = timezone.now()
        return now >= self.start_date + datetime.timedelta(minutes=30)
    
    def is_on_confirmation_period(self):
        now = timezone.now()
        period_days = datetime.timedelta(days=self.activity.confirmation_period)
        return self.start_date - period_days <= now and not self.has_finished()

    def can_user_join(self, user):
        return self.activity.author != user and self.activity.attendants.filter(id=user.id).exists() and not self.confirmed_attendants.filter(id=user.id).exists()
    