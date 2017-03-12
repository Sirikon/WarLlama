# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from Alpaca.storage import *
from Alpaca.file_paths import *
from Alpaca.emails import *

from group_model import Group

import hashlib
import random
import datetime
import re #RegEx


class Event (models.Model): 
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    cover = models.ImageField( upload_to=event_cover_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=no_cover_path )

    banner = models.ImageField( upload_to=event_banner_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=no_banner_path )

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=5000)
    city = models.TextField(max_length=100)
    pub_date = models.DateTimeField('publication date')
    
    start_date = models.DateTimeField('start date', default=timezone.now)
    end_date = models.DateTimeField('end date', default=timezone.now)
    age_minimum = models.IntegerField(default=0)
   
    attendants = models.ManyToManyField(User, related_name="attending_events", blank=True)
    num_attendants = models.IntegerField(default=0)

    pending_attendants = models.ManyToManyField(User, related_name="waiting_events", blank=True)

    # Settings   
    show_title = models.BooleanField(default=True)
    group_only_attendants = models.BooleanField(default=False)
    auto_register_users = models.BooleanField(default=True)
    auto_register_activities = models.BooleanField(default=False) 


    ## ---------------------------------        
    ## -- STRINGs
    def __str__(self):
        return self.pub_date.strftime('(%Y-%m-%d, %H:%M)') + " " + self.title + " - Group: " + self.group.name

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.title, d=self.description)

    ## -- GETs    
    def is_user_old_enough(self, user):
        # http://stackoverflow.com/questions/2217488/age-from-birthdate-in-python/9754466#9754466
        today = timezone.now()
        born = user.profile.birth_date
        years_difference = today.year - born.year
        is_before_birthday = (today.month, today.day) < (born.month, born.day)
        elapsed_years = years_difference - int(is_before_birthday)
        return elapsed_years >= self.age_minimum

    def is_user_attending(self, user):
        return user in self.attendants.all() or user in self.group.admin_list.all() or user == self.group.superuser

    def get_short_description(self):
        temp = re.sub("(<img)(?<=(<img)).*?(?=>)(>)", " ", self.description)

        if len(temp) > 200:
            temp = temp[:200]
            
        return temp
    
    ## -- SETs
    def new(self, pub_date, group):
        self.pub_date = pub_date
        self.group = group       
        self.save()  
        #TO-DO: email_registered_your_new_event(event) to group mail

    def edit(self, cover, banner):
        self.set_cover(cover)
        self.set_banner(banner)

    def set_cover(self, cover):       
        self.cover = cover
        self.save()  

    def set_banner(self, cover):       
        self.banner = banner
        self.save()  

    def add_attendant(self, user):
        self.attendants.add(user)
        self.pending_attendants.remove(user)
        self.num_attendants = self.attendants.count()
        self.save()

    def remove_attendant(self, user):
        self.attendants.remove(user)
        self.pending_attendants.remove(user)
        self.num_attendants = self.attendants.count()
        self.save()
        for activity in self.activity_list.all():
            if user is activity.author:
                if activity.end_date > timezone.now():
                    self.activity_list.remove(activity)
            else:
                activity.remove_attendant(user)

    def add_activity(self, activity):
        activity.pending_event = None
        activity.event = self
        activity.save()

    ## -- USER ACTIONs
    def join(self, user):
        if self.group_only_attendants and user not in self.group.member_list.all():
            return

        if self.auto_register_users:
            self.attendants.add(user)
            self.num_members = self.attendants.count()
            #TO-DO: email_user_acted_on_your_activity(group, user, True)
        else:
            self.pending_attendants.add(user)
            #TO-DO: email_user_requested_to_join(group, user)
        self.save()

    def leave(self, user):
        self.remove_attendant(user)
        #TO-DO: email_user_acted_on_your_activity(group, user, False)

    def kick(self, user):
        self.remove_attendant(user)
        #TO-DO: email_you_were_kicked_out_from_group(self, selected_user)

    def handle_user_request(self, user, is_accepted):
        if is_accepted:
            self.add_attendant(user)
            #TO-DO: email_your_request_was_handled(self, user, True)
        else:
            self.pending_attendants.remove(user)   
            #TO-DO: email_your_request_was_handled(self, user, False)
            
        self.num_attendants = self.attendants.count()
        self.save()
   
    def handle_activity_request(self, activity, is_accepted):
        if is_accepted:
            self.add_activity(activity)
            #TO-DO: email_your_request_was_handled(self, user, True)
        else:
            activity.pending_event = None  
            #TO-DO: email_your_request_was_handled(self, user, False)
        activity.save()
        self.save()
