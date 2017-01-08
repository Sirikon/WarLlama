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
from event_model import Event

import hashlib
import random
import datetime
import re #RegEx


class Activity (models.Model):
    cover = models.ImageField( upload_to=activity_cover_path, 
                               storage=OverwriteStorage(),
                               null=True, blank=True,
                               default=no_cover_path )

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=5000)
    city = models.TextField(max_length=100)
    pub_date = models.DateTimeField('publication date')
   
    group = models.ForeignKey(Group, related_name="activity_list", blank=True, null=True)
    pending_group = models.ForeignKey(Group, related_name="pending_activities", blank=True, null=True)
    
    event = models.ForeignKey(Event, related_name="activity_list", blank=True, null=True)
    pending_event = models.ForeignKey(Event, related_name="pending_activities", blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_activities")
    attendants = models.ManyToManyField(User, related_name="attending_activities", blank=True)
    num_attendants = models.IntegerField(default=0)
    pending_attendants = models.ManyToManyField(User, related_name="waiting_activities", blank=True)

    # Settings
    auto_register = models.BooleanField(default=False)
    confirmation_period = models.IntegerField(default=3, validators=[MinValueValidator(3)])
    age_minimum = models.IntegerField(default=0)

    ## ---------------------------------
    ## -- STRINGs
    def __str__(self):
        return self.pub_date.strftime('(%Y-%m-%d, %H:%M)') + " " + self.title + " - Author: " + self.author.username

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.title, d=self.description)
        
    ## -- GETs
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


    ## -- SETs
    def set_cover(self, new_cover):
        self.cover = new_cover
        self.save()

    def set_group(self, new_group):
        if new_group is None:
            self.group = None
        else:
            if new_group.auto_register_activities:
                self.group = new_group
                #TO-DO: email to group
            else:
                self.pending_group = new_group
                self.group = None
                #TO-DO: email to group - pending activities
        self.save()  

    def remove_attendant(self, user):
        self.attendants.remove(user)
        self.num_attendants = self.attendants.count()
        self.save()
        for session in self.session_set.all():
            if not session.has_finished():
                session.confirmed_attendants.remove(user)
                session.save()

    ## -- USER ACTIONs
    def new(self, pub_date, new_author):
        self.pub_date = pub_date
        self.author = new_author
        self.save()  
        email_registered_your_new_activity(self)  

    def edit(self, cover, new_group):
        self.set_cover(new_cover)
        self.set_group(new_group)
        self.save()  

        self.save() 
        for attendant in self.attendants.all():
            email_activity_got_updated(self, attendant)

    def join(self, user):
        if self.auto_register:
            self.attendants.add(user)
            self.num_attendants = self.attendants.count()
            email_user_acted_on_your_activity(self, user, True)
        else:
            self.pending_attendants.add(user)
            email_user_requested_to_join(self, user)
        self.save()

    def leave(self, user):
        self.remove_attendant(user)
        email_user_acted_on_your_activity(self, user, False)
    
    def kick(self, user):
        self.remove_attendant(user)
        email_you_were_kicked_out_from_activity(self, user)

    def handle_user_request(self, user, is_accepted):
        if is_accepted:
            self.attendants.add(user)
            self.pending_attendants.remove(user)
            email_your_request_was_handled(self, user, True)
        else:
            self.pending_attendants.remove(user)   
            email_your_request_was_handled(self, user, False)
            
        self.num_attendants = self.attendants.count()
        self.save()
