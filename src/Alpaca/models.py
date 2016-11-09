from __future__ import unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User

import datetime

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateTimeField('date of birth')
    reg_date = models.DateTimeField('date registered')

    def __str__(self):
        return user.username


class Activity (models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    pub_date = models.DateTimeField('publication date', default=datetime.datetime.now())
   
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_activities")
    attendants = models.ManyToManyField(User, related_name="attending_activities", blank=True)

    # Settings
    auto_register = models.BooleanField(default=False)
    confirmation_period = models.IntegerField(default=3, validators=[MinValueValidator(3)])
    age_minimum = models.IntegerField(default=0)

    def __str__(self):
        return self.pub_date.strftime('(%Y-%m-%d, %H:%M)') + " " + self.title + " - Author: " + self.author.username + " - Attendants #" + str(self.attendants.count())


class Session (models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)

    date = models.DateTimeField('start time')
    end_time = models.TimeField('end time (approx.)')

    place = models.CharField(max_length=100)
    confirmed_attendants = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.description + " - " + self.date.strftime('%Y-%m-%d, from %H:%M') + " " + self.end_time.strftime('to %H:%M') + " - " + str(self.confirmed_attendants.count()) + " confirmed attending." 
    