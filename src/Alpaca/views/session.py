from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.utils import timezone
from django.contrib.auth.models import User

from ..models import Activity, Session
from ..forms import SessionForm

import datetime

## -- SESSIONS -- ##
def new_session(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    user = request.user
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    context = { 'form_title': "Create a new session",
                'submit_text': "Create!",
                'rich_field_name': "description" }

    if request.method == "POST":
        form = SessionForm(data=request.POST)
        if form.is_valid():
            session = form.save(commit=False)    
            session.activity = activity
            session.save()    
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/form_layout.html', context)

    else:
        context['form'] = SessionForm()
        return render(request, 'Alpaca/form_layout.html', context)


def edit_session(request, activity_id, session_id):
    user = request.user
    activity = get_object_or_404(Activity, id=activity_id)   
    session = get_object_or_404(Session, id=session_id)   

    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))    

    context = { 'form_title': "Editing a session",
                'submit_text': "Save changes",
                'rich_field_name': "description" }

    if request.method == "POST":
        form = SessionForm(data=request.POST, instance=session)
        if form.is_valid():
            form.save()   
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/form_layout.html', context)

    else:
        context['form'] = SessionForm(instance=session)
        return render(request, 'Alpaca/form_layout.html', context)


def confirm_session(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        if user in activity.attendants.all():
            session = get_object_or_404(Session, id=request.POST.get("session_id"))
            if activity == session.activity and session.is_on_confirmation_period():
                session.confirmed_attendants.add(user)
                session.save()
                # TO-DO --> Send "User has confirmed assistance" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


