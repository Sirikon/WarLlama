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
                               default=event_no_banner_path )

    title = models.CharField(max_length=200)
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

    # -- GETs
    def get_short_description(self):
        temp = re.sub("(<img)(?<=(<img)).*?(?=>)(>)", " ", self.description)

        if len(temp) > 200:
            temp = temp[:200]
            
        return temp
    
    # -- SETs
    def remove_attendant(user):
        self.attendants.remove(user)
        self.num_attendants = self.attendants.count()
        self.save()
        for activity in self.activity_list.all():
            activity.remove_attendant(user)




