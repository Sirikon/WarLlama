from django.db.models import Count, Q

from django.utils import translation
from django import http
from django.conf import settings

from ..models import *

import hashlib
import random

# Useful functions for the views. These functions return contexts.
def generate_token():
    hash_object = hashlib.sha256(str(random.randint(1, 1000)))
    hex_dig = hash_object.hexdigest()
    return hex_dig

def set_translation(request): 
    if request.user.is_authenticated():
        user_language = request.user.profile.language_preference   
    else: 
        user_language = "en"
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language

def sort_activity_table(activity_list, sort_column, last_column):
    sort_sign = "-"

    if sort_column != None and sort_column != "":        
        if last_column != None and sort_column != "":
            if last_column[0] == "-":
                if sort_column == last_column[1:]:
                    sort_sign = ""
        
        if sort_column == "next_session":
            sorted_list = sorted(activity_list.all(), key= lambda a: (a.get_next_session().start_date), reverse=(sort_sign=="-"))

        else:
            sorted_list = activity_list.order_by(sort_sign + sort_column)
    else: 
         sorted_list = activity_list.order_by('-pub_date')
         sort_column = "pub_date"
    
    icon_name = "fa-sort-desc"
    if sort_sign == "-":
        icon_name = "fa-sort-asc"

    context = { 'activity_list': sorted_list,
                'sort_sign': sort_sign,
                'sorted_column': sort_column,
                'sort_icon': icon_name }

    return context


