from __future__ import unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateTimeField('date of birth')
    reg_date = models.DateTimeField('date registered')

    def __str__(self):
        return user.username


class Activity (models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
   
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_activities")
    attendants = models.ManyToManyField(User, related_name="attending_activities")

    # Settings
    auto_register = models.BooleanField(default=False)
    confirmation_period = models.IntegerField(default=3, validators=[MinValueValidator(3)])
    age_minimum = models.IntegerField(default=0)


class Session (models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)

    date = models.DateTimeField('session date')
    end_time = models.TimeField('session duration')

    place = models.CharField(max_length=100)
    confirmed_attendants = models.ManyToManyField(User)
    