from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile, Group, Event, Activity
from ..forms import EventForm
from ..emails import email_reset_password

from ..utils import set_translation, sort_activities

import datetime


def event(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    to_sort_column = request.GET.get('order_by')
    sorted_column = request.GET.get('last')
    context = sort_activities(Activity.objects.filter(event_id=event.id), to_sort_column, sorted_column)

    context['user'] = request.user
    context['event'] = event

    if user.is_authenticated:
        if user == event.group.superuser or user in event.group.admin_list.all():
            return render(request, 'Alpaca/event/event_admin.html', context)
        else:
            return render(request, 'Alpaca/event/event_user.html', context)
    else:        
        return render(request, 'Alpaca/event/event_anon.html', context)

def new_event(request, group_id):
    set_translation(request)
    
    user = request.user
    group = get_object_or_404(Group, pk=group_id)

    print("Superuser? " + str(user == group.superuser))

    if not user.is_authenticated() or (user != group.superuser and user not in group.admin_list.all()):
        return  HttpResponseRedirect(reverse('alpaca:index'))
    

    context = { 'form_title': _("Start a new event!"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)    
            event.pub_date = timezone.now()
            event.group = group            
            event.cover = form.cleaned_data["cover"]
            event.banner = form.cleaned_data["banner"]
            event.save()  
            #email_registered_your_new_activity(activity)  
            return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = EventForm() 
        return render(request, 'Alpaca/_form_layout.html', context)


def edit_event(request, event_id):
    set_translation(request)
    user = request.user
    event = get_object_or_404(Event, pk=event_id)
    if not user.is_authenticated() or (user != event.group.superuser and user not in event.group.admin_list.all()):
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Editing event") + " " + event.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save(commit=False)   
            event.cover = form.cleaned_data["cover"]
            event.banner = form.cleaned_data["banner"]
            event.save() 
            return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = EventForm(instance=event)
        return render(request, 'Alpaca/_form_layout.html', context)


## USER ACTIONS ##
def join_event(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if request.method == "POST":
        if event.auto_register_users:
            event.attendants.add(user)
            event.num_members = event.attendants.count()
            #TO-DO: email_user_acted_on_your_activity(group, user, True)
        else:
            event.pending_attendants.add(user)
            #TO-DO: email_user_requested_to_join(group, user)
        event.save()

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))


def leave_event(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if request.method == "POST":
        event.remove_attendant(user)
        #TO-DO: email_user_acted_on_your_activity(group, user, False)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))

## ADMIN ACTIONS ##
def kick_attendant(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        event.remove_attendant(selected_user)
        #TO-DO: email_you_were_kicked_out_from_activity(activity, selected_user)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))


def pending_attendants(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        if "accept_request" in request.POST:
            event.attendants.add(selected_user)
            event.pending_attendants.remove(selected_user)
            #TO-DO: email_your_request_was_handled(group, selected_user, True)

        elif "reject_request" in request.POST:
            event.pending_attendants.remove(selected_user)   
            #TO-DO: email_your_request_was_handled(group, selected_user, False)
        
        event.num_members = event.attendants.count()
        event.save()

    return HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))

def pending_activities(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_activity = get_object_or_404(Activity, id=request.POST.get("activity_request"))
        if "accept_request" in request.POST:
            selected_activity.pending_event = None
            selected_activity.event = event
            #TO-DO: email_your_request_was_handled(group, selected_user, True)

        elif "reject_request" in request.POST:
            selected_activity.pending_event = None  
            #TO-DO: email_your_request_was_handled(group, selected_user, False)
        selected_activity.save()

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))
