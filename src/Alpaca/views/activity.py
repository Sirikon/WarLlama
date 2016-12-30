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
from .emails import *

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
    
    temp_list = list(chain(user.member_of.all(), user.admin_of.all(), Group.objects.filter(superuser=user)))
    temp_list = sorted(temp_list, key=lambda group: group.name)
    user_groups= [(-1, "(No group)")]
    for group in temp_list:
        user_groups.append([group.id, group.name])
    
    context = { 'form_title': _("Start a new activity"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(group_options=user_groups, data=request.POST)
        if form.is_valid():
            activity = form.save(commit=False)    
            activity.pub_date = timezone.now()
            activity.author = user

            group_id = form.cleaned_data["group_options"]
            if group_id > 0:
                group = get_object_or_404(Group, id=group.id)
                if group.auto_register_activities:
                    activity.group = group
                    #TO-DO: email to group
                else:
                    activity.pending_group = group
                    #TO-DO: email to group - pending activities
            activity.save()  

            email_registered_your_new_activity(activity)  
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
 
    temp_list = list(chain(user.member_of.all(), user.admin_of.all(), Group.objects.filter(superuser=user)))
    temp_list = sorted(temp_list, key=lambda group: group.name)
    user_groups= [(-1, "(No group)")]
    for group in temp_list:
        user_groups.append([group.id, group.name])
    
    context = { 'form_title': _("Editing activity") + " " + activity.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)   
            activity.cover = form.cleaned_data["cover"]
            
            group_id = form.cleaned_data["group_options"]
            if group_id > 0:
                group = get_object_or_404(Group, id=group.id)
                if group.auto_register_activities:
                    activity.group = group
                    #TO-DO: email to group
                else:
                    activity.pending_group = group
                    #TO-DO: email to group - pending activities

            activity.save() 
            for attendant in activity.attendants.all():
                email_activity_got_updated(activity, attendant)

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
        if activity.auto_register:
            activity.attendants.add(user)
            activity.num_attendants = activity.attendants.count()
            email_user_acted_on_your_activity(activity, user, True)
        else:
            activity.pending_attendants.add(user)
            email_user_requested_to_join(activity, user)
        activity.save()

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def leave_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.remove_attendant(user)
        email_user_acted_on_your_activity(activity, user, False)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def kick_attendant(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        activity.remove_attendant(selected_user)
        email_you_were_kicked_out_from_activity(activity, selected_user)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def pending_requests(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        if "accept_request" in request.POST:
            activity.attendants.add(selected_user)
            activity.pending_attendants.remove(selected_user)
            email_your_request_was_handled(activity, selected_user, True)

        elif "reject_request" in request.POST:
            activity.pending_attendants.remove(selected_user)   
            email_your_request_was_handled(activity, selected_user, False)
        
        activity.num_attendants = activity.attendants.count()
        activity.save()

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
