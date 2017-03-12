from django.db.models import Count, Q

from django.utils import translation
from django import http
from django.conf import settings

from itertools import chain
from operator import attrgetter

from models import *

import random
import re



# Useful functions for the views. These functions return contexts.
def set_translation(request): 
    if request.user.is_authenticated():
        user_language = request.user.profile.language_preference   
    else: 
        user_language = "en"
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language

def handle_form(sent_form, request, context, on_success_address, on_success_kwargs, on_failure_render):
    form = sent_form
    if form.is_valid():
        item = form.save()        
        return  HttpResponseRedirect(reverse('alpaca:' + on_success_address, kwargs=on_success_kwargs))
    else:
        context['form'] = sent_form
        return render(request, on_failure_render, context)





# FILTER  & SORT FUNCTIONS
def filter_activities(request, user, user_filter, activity_list):
    if user.is_authenticated: # Can't filter for anons
        if user_filter == "author":
            activity_list = list(user.owned_activities.all())
        elif user_filter == "attendant":
            activity_list = list(user.attending_activities.all())

    return activity_list  

def filter_groups(request, user, user_filter, group_list):
    if user.is_authenticated: # Can't filter for anons
        if user_filter == "admin":
            group_list = list(chain(user.admin_of.all(), user.superuser_of.all()))
        elif user_filter == "member":
            group_list = list(user.member_of.all())

    return group_list

def sort_activities(activity_list, sort_column, last_column):
    sort_sign = "-"

    if activity_list is not list:
        activity_list = list(activity_list)

    if sort_column != None and sort_column != "":        
        if last_column != None and sort_column != "":
            if last_column[0] == "-":
                if sort_column == last_column[1:]:
                    sort_sign = ""
        
        if sort_column == "next_session":
            has_sessions_list = filter(lambda a: a.get_next_session() != None, act)
            sorted_list = sorted(has_sessions_list, key= lambda a: (a.get_next_session() or None ), reverse=(sort_sign=="-"))

        else:
            sorted_list = sorted(activity_list, key= attrgetter(sort_column), reverse=(sort_sign=="-"))
    else: 
         sorted_list = sorted(activity_list, key= lambda a: a.pub_date, reverse=True)
         sort_column = "pub_date"
    
    icon_name = "fa-sort-desc"
    if sort_sign == "-":
        icon_name = "fa-sort-asc"

    context = { 'activity_list': sorted_list,
                'sort_sign': sort_sign,
                'sorted_column': sort_column,
                'sort_icon': icon_name }

    return context


# SEARCH FUNCTIONS - Courtesy of http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

    
def search(request, query_name, models, search_fields):
    # Adapted 
    query_string = ''
    found_entries = None

    if (query_name in request.GET) and request.GET[query_name].strip():
        query_string = request.GET[query_name]
        
        entry_query = get_query(query_string, search_fields)
        
        found_entries = {}
        for model in models:
            chain(found_entries, model.objects.filter(entry_query))
    
    return found_entries