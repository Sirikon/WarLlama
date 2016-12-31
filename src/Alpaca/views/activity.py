from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse

from django.utils import timezone
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from itertools import chain

from ..models import Activity, Session
from ..forms import ActivityForm
from .utils import set_translation

import datetime


## -- ACTIVITIES -- ##
def activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user
    session_list = activity.session_set.order_by('start_date')
    context = { 'user': user,
                'activity': activity,
                'session_list': session_list}

    if user.is_authenticated:
        context['user_is_old_enough'] = activity.is_user_old_enough(user)
        if user == activity.author:
            return render(request, 'Alpaca/activity/activity_author.html', context)
        else:
            return render(request, 'Alpaca/activity/activity_user.html', context)
    else:        
        return render(request, 'Alpaca/activity/activity_anon.html', context)


def new_activity(request):
    set_translation(request)
    
    user = request.user
    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    user_groups = [(-1, "(No group)")]
    for group in user.get_groups():
        user_groups.append([group.id, group.name])
    
    context = { 'form_title': _("Start a new activity"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(group_options=user_groups, data=request.POST)
        if form.is_valid():
            activity = form.save(commit=False)  
            cover = form.cleaned_data["cover"]
            group_id = form.cleaned_data["group_options"]
            group = None
            if group_id > 0: group = get_object_or_404(Group, id=group.id)

            activity.new(timezone.now(), user, cover, group)  

            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = ActivityForm(group_options=user_groups) 
        return render(request, 'Alpaca/_form_layout.html', context)


def edit_activity(request, activity_id):
    set_translation(request)
    user = request.user
    activity = get_object_or_404(Activity, pk=activity_id)
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
 
    user_groups = [(-1, "(No group)")]
    for group in user.get_groups():
        user_groups.append([group.id, group.name])
    
    context = { 'form_title': _("Editing activity") + " " + activity.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)   
            cover = form.cleaned_data["cover"]
            group_id = form.cleaned_data["group_options"]
            group = None
            if group_id > 0:  group = get_object_or_404(Group, id=group.id)

            activity.edit(cover, group)          

            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = ActivityForm(instance=activity)
        return render(request, 'Alpaca/_form_layout.html', context)

def join_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def leave_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.leave(user)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def kick_attendant(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        activity.kick(selected_user)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def pending_requests(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        activity.handle_user_request(selected_user, "accept_request" in request.POST)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
