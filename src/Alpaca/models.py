# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import datetime

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateTimeField('date of birth')

    def __str__(self):
        return self.user.username

class Activity (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=5000)
    pub_date = models.DateTimeField('publication date')
   
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_activities")
    attendants = models.ManyToManyField(User, related_name="attending_activities", blank=True)
    pending_attendants = models.ManyToManyField(User, related_name="waiting_activities", blank=True)

    # Settings
    auto_register = models.BooleanField(default=False)
    confirmation_period = models.IntegerField(default=3, validators=[MinValueValidator(3)])
    age_minimum = models.IntegerField(default=0)

    def __str__(self):
        return self.pub_date.strftime('(%Y-%m-%d, %H:%M)') + " " + self.title + " - Author: " + self.author.username

    def __unicode__(self):
        return u'{t}/{d}'.format(t=self.title, d=self.description)

    def is_user_old_enough(self, user):
        # http://stackoverflow.com/questions/2217488/age-from-birthdate-in-python/9754466#9754466
        today = timezone.now()
        born = user.profile.birth_date
        years_difference = today.year - born.year
        is_before_birthday = (today.month, today.day) < (born.month, born.day)
        elapsed_years = years_difference - int(is_before_birthday)
        return elapsed_years >= self.age_minimum


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
    