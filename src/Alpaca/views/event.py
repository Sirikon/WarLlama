from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

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
        context['user_is_old_enough'] = event.is_user_old_enough(user)
        if user == event.group.superuser or user in event.group.admin_list.all():
            return render(request, 'Alpaca/event/event_admin.html', context)
        else:
            return render(request, 'Alpaca/event/event_user.html', context)
    else:        
        return render(request, 'Alpaca/event/event_anon.html', context)

@login_required
def new_event(request, group_id):
    set_translation(request)
    
    user = request.user
    group = get_object_or_404(Group, pk=group_id)

    if user != group.superuser and user not in group.admin_list.all():
        return  HttpResponseRedirect(reverse('alpaca:index'))
    

    context = { 'form_title': _("Start a new event!"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save_new(group)                     
            return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = EventForm() 
        return render(request, 'Alpaca/_form_layout.html', context)


@login_required
def edit_event(request, event_id):
    set_translation(request)
    user = request.user
    event = get_object_or_404(Event, pk=event_id)
    
    if user != event.group.superuser and user not in event.group.admin_list.all():
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Editing event") + " " + event.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = EventForm(instance=event)
        return render(request, 'Alpaca/_form_layout.html', context)


## USER ACTIONS ##
@login_required
def join_event(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if request.method == "POST":
        event.join(user)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))


@login_required
def leave_event(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if request.method == "POST":
        event.leave(user)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))

## ADMIN ACTIONS ##
@login_required
def event_kick_attendant(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        event.kick(selected_user)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))


@login_required
def event_pending_attendants(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        event.handle_user_request(selected_user, "accept_request" in request.POST)

    return HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))


@login_required
def event_pending_activities(request, event_id):
    set_translation(request)
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        selected_activity = get_object_or_404(Activity, id=request.POST.get("activity_request"))
        event.handle_activity_request(selected_activity, "accept_request" in request.POST)

    return  HttpResponseRedirect(reverse('alpaca:event', kwargs={'event_id': event_id}))
