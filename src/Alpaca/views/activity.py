from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse

from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from itertools import chain

from ..models import Activity, Session
from ..forms import ActivityForm
from ..utils import set_translation, handle_form

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
        context['user_has_actions'] = True

        if activity.pending_event != None:
            context['user_has_actions'] = False
            context['why_not_message'] = _("This activity is waiting to be part of an event! Come back later :)")        

        elif activity.event != None and not activity.event.is_user_attending(user):
            context['user_has_actions'] = False
            context['why_not_message'] = _("This activity is part of an event. Join the event to attend this activity!")        
            
        elif not activity.is_user_old_enough(user):
            context['user_has_actions'] = False
            context['why_not_message'] = _("You are too young to attend this activity.")

        elif user in activity.pending_attendants.all():
            context['user_has_actions'] = False
            context['why_not_message'] = _("The author of this activity has received your request to join!") 

        if user == activity.author:
            return render(request, 'Alpaca/activity/activity_author.html', context)
        else:
            return render(request, 'Alpaca/activity/activity_user.html', context)
    else:        
        return render(request, 'Alpaca/activity/activity_anon.html', context)

@login_required
def new_activity(request):
    set_translation(request)    
    user = request.user    

    context = { 'form_title': _("Start a new activity"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    user_groups = user.profile.get_groups()

    if request.method == "POST":
        form = ActivityForm(user_groups, request.POST, request.FILES )
        if form.is_valid():
           activity = form.save_new(user)        
           return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id} ))
        else:
           context['form'] = form
           return render(request, 'Alpaca/_form_layout.html', context)
    else:
        context['form'] = ActivityForm(group_list=user_groups) 
        return render(request, 'Alpaca/_form_layout.html', context)


@login_required
def edit_activity(request, activity_id):
    set_translation(request)
    user = request.user
    activity = get_object_or_404(Activity, pk=activity_id)
    if user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
 
    if activity.group != None or activity.pending_group != None:
        user_groups = [activity.group.id]
    else:
        user_groups = user.profile.get_groups()
    
    context = { 'form_title': _("Editing activity") + " " + activity.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(user_groups, request.POST, request.FILES, instance=activity)
        if form.is_valid():
           activity = form.save()   
           return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id} ))
        else:
           context['form'] = form
           return render(request, 'Alpaca/_form_layout.html', context)
    else:
        context['form'] = ActivityForm(group_list=user_groups, instance=activity) 
        return render(request, 'Alpaca/_form_layout.html', context)


@login_required
def join_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.join(user)

    return HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


@login_required
def leave_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.leave(user)

    return HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


@login_required
def activity_kick_attendant(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        activity.kick(selected_user)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


@login_required
def activity_pending_requests(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        activity.handle_user_request(selected_user, "accept_request" in request.POST)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
