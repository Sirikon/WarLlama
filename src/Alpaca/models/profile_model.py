# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

from itertools import chain

from Alpaca.storage import *
from Alpaca.file_paths import *
from Alpaca.emails import *

import hashlib
import random
import datetime
import re #RegEx


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

    
    ## ---------------------------------        
    ## -- STRINGs
    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return u'{fn}/{ln}'.format(fn=self.user.first_name, ln=self.user.last_name)

    # -- GETs
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
    
    def get_groups(self):        
        temp_list = list(chain( self.user.member_of.all(), 
                                self.user.admin_of.all(), 
                                self.user.superuser_of.all()))
        temp_list = sorted(temp_list, key=lambda group: group.name)

        id_list = []
        for g in temp_list:
            id_list.append(g.id)

        return id_list

    # -- SETs
    def set_avatar(self, new_avatar):
        self.avatar = new_avatar
        self.save()
        
    def generate_token(self):
        hash_object = hashlib.sha256(str(random.randint(1, 1000)))
        self.current_token = hash_object.hexdigest()
        self.save()

    def activate(self):
        self.user.is_active = True
        self.user.save()
        self.generate_token() # For security, a new token is created.
