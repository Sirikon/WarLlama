from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse

from django.utils import timezone
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Activity, Session
from ..forms import ActivityForm
from .utils import set_translation

import datetime

## -- ACTIVITIES -- ##
def new_activity(request):
    set_translation(request)
    
    user = request.user
    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    context = { 'form_title': _("Start a new activity"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(data=request.POST)
        if form.is_valid():
            activity = form.save(commit=False)    
            activity.pub_date = timezone.now()
            activity.author = user
            activity.save()    
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = ActivityForm() 
        return render(request, 'Alpaca/_form_layout.html', context)


def edit_activity(request, activity_id):
    set_translation(request)
    user = request.user
    activity = get_object_or_404(Activity, pk=activity_id)
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Editing activity") + " " + activity.title,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = ActivityForm(data=request.POST, instance=activity)
        if form.is_valid():
            form.save()   
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = ActivityForm(instance=activity)
        return render(request, 'Alpaca/_form_layout.html', context)


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
            return render(request, 'Alpaca/activity_author.html', context)
        else:
            return render(request, 'Alpaca/activity_user.html', context)
    else:        
        return render(request, 'Alpaca/activity_anon.html', context)


def join_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        if activity.auto_register:
            activity.attendants.add(user)
            activity.num_attendants = activity.attendants.count()
        else:
            activity.pending_attendants.add(user)
        activity.save()
        # TO-DO --> Send "User has join your activity" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def leave_activity(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.attendants.remove(user)
        activity.num_attendants = activity.attendants.count()
        activity.save()
        for session in activity.session_set.all():
            if not session.has_finished():
                session.confirmed_attendants.remove(user)
                session.save()
                # TO-DO --> Send "User has left your activity" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def kick_attendant(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        activity.attendants.remove(selected_user)
        activity.num_attendants = activity.attendants.count()
        activity.save()
        for session in activity.session_set.all():
            if not session.has_finished():
                session.confirmed_attendants.remove(selected_user)
                session.save()
                # TO-DO --> Send "You have been kicked from activity" email to kicked user

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def pending_requests(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        if "accept_request" in request.POST:
            activity.attendants.add(selected_user)
            activity.pending_attendants.remove(selected_user)

        elif "reject_request" in request.POST:
            activity.pending_attendants.remove(selected_user)   
        
        activity.num_attendants = activity.attendants.count()
        activity.save()
        # TO-DO --> Send "You have pending requests" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
