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

from activity_model import Activity

import hashlib
import random
import datetime
import re #RegEx


class Session (models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    description = models.TextField(max_length=500)

    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

    location = models.CharField(max_length=100)
    confirmed_attendants = models.ManyToManyField(User, blank=True)
    emails_are_sent = models.BooleanField(default=False)

    ## ---------------------------------
    ## -- STRINGs
    def __str__(self):
        return self.description + " - " + self.start_date.strftime('%Y-%m-%d, from %H:%M') + " " + self.end_date.strftime('to %Y-%m-%d, %H:%M') 

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.activity.title, d=self.description)
    
    ## -- GETs
    def has_finished(self):
        now = timezone.now()
        return now >= self.start_date + datetime.timedelta(minutes=30)
    
    def is_on_confirmation_period(self):
        now = timezone.now()
        period_days = datetime.timedelta(days=self.activity.confirmation_period)
        return self.start_date - period_days <= now and not self.has_finished()

    def can_user_join(self, user):
        return self.activity.author != user and self.activity.attendants.filter(id=user.id).exists() and not self.confirmed_attendants.filter(id=user.id).exists()
    

    ## -- SETs
    def new(activity):
        self.activity = activity
        self.safe()        
        for attendant in activity.attendants.all():
            email_activity_new_sessions(activity, attendant)
    
    def confirm(user):
        if self.is_on_confirmation_period() and user in self.activity.attendants.all():
            self.confirmed_attendants.add(user)
            self.save()
            email_user_confirmed_assistance(self.activity, self, user)