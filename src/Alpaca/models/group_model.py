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

import hashlib
import random
import datetime
import re #RegEx


class Group (models.Model):
    logo = models.ImageField( upload_to=group_logo_path, 
                                storage=OverwriteStorage(),
                                null=True, blank=True,
                                default="no-logo.png")
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=200)
    email = models.EmailField(max_length=254)

    superuser = models.ForeignKey(User, related_name="superuser_of")
    admin_list = models.ManyToManyField(User, related_name="admin_of", blank=True)
    member_list = models.ManyToManyField(User, related_name="member_of", blank=True)
    total_num_members = models.IntegerField(default=0)

    pending_members = models.ManyToManyField(User, related_name="waiting_groups", blank=True)

    creation_date = models.DateTimeField('creation date')

    # Settings
    show_email = models.BooleanField(default=True)
    auto_register_users = models.BooleanField(default=False)
    auto_register_activities = models.BooleanField(default=False)

    ## ---------------------------------
    ## -- STRINGs
    def __str__(self):
        return self.name + " - #" + str(1 + self.admin_list.count() + self.member_list.count())

    ## -- GETs
    def member_count(self):
        return  1 + self.admin_list.count() + self.member_list.count()

    def get_short_description(self):
        temp = re.sub("(<img)(?<=(<img)).*?(?=>)(>)", " ", self.description)

        if len(temp) > 200:
            temp = temp[:200]
            
        return temp

    ## -- SETs
    def new(self, creation_date, user):
        self.creation_date = creation_date
        self.superuser = user
        self.total_num_members = 1
        self.save()  
        #TO-DO: email_registered_your_new_group(group)
    
    def edit(self, logo):
        self.set_logo(logo)
        #TO-DO: email to all members - change at group (SPAM)

    def set_logo(self, logo):
        self.logo = logo
        self.save()          
    
    def add_member(self, user):
        self.member_list.add(user)
        self.pending_members.remove(user)
        self.total_num_members = self.member_count()
        self.save()

    def remove_member(self, user):
        if user is self.superuser:
            self.superuser = self.admin_list.all()[:1].get()
            # TO-DO: Email you're the new superuser of the group
        elif user in self.admin_list.all():
            self.admin_list.remove(user)
        else:
            self.member_list.remove(user)
            for event in self.event_set.all():
                if event.group_only_attendants and event.start_date > timezone.now():
                    event.remove_attendant(user)
          
        self.total_num_members = self.member_count()      
        self.save()

    def set_member_rights(self, user, to_admin):
        if to_admin:
            self.admin_list.add(user)
            self.member_list.remove(user)
        else:
            self.member_list.add(user)
            self.admin_list.remove(user)
        self.save()
 


    ## -- USER ACTIONs
    def join(self, user):
        if self.auto_register_users:
            self.add_member(user)
            #TO-DO: email_user_acted_on_your_group(self, user, True)
        else:
            self.pending_members.add(user)
            #TO-DO: email_user_requested_to_join(self, user)
        self.save()

    def leave(self, user):
        self.remove_member(user)
        #TO-DO: email_user_acted_on_your_activity(group, user, False)
    
    def kick(self, user):
        self.remove_member(user)
        #TO-DO: email_you_were_kicked_out_from_group(self, selected_user)

    def promote(self, user):
        self.set_member_rights(user, to_admin=True)
        #TO-DO: email you were promoted to admin at group 

    def demote(self, user):
        self.set_member_rights(user, to_admin=False)
        #TO-DO: email you were demoted to member at group 

    def handle_user_request(self, user, is_accepted):
        if is_accepted:
            self.add_member(user)
            #TO-DO: email_your_request_was_handled(self, user, True)
        else:
            self.pending_members.remove(user)   
            #TO-DO: email_your_request_was_handled(self, user, False)
            
        self.total_num_members = self.member_count()
        self.save()
   
    def handle_activity_request(self, activity, is_accepted):
        if is_accepted:
            activity.pending_group = None
            activity.group = self
            #TO-DO: email_your_request_was_handled(self, user, True)
        else:
            activity.group = None
            activity.pending_group = None  
            #TO-DO: email_your_request_was_handled(self, user, False)
        activity.save()
        self.save()
