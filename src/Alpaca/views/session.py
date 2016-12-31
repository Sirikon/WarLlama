from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Activity, Session
from ..forms import SessionForm

from .utils import set_translation
from .emails import *

import datetime

## -- SESSIONS -- ##
def new_session(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, id=activity_id)
    user = request.user
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    context = { 'form_title': _("Create a new session"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = SessionForm(data=request.POST)
        if form.is_valid():
            session = form.save(commit=False)    
            session.new(activity)
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = SessionForm()
        return render(request, 'Alpaca/_form_layout.html', context)


def edit_session(request, activity_id, session_id):
    set_translation(request)
    user = request.user
    activity = get_object_or_404(Activity, id=activity_id)   
    session = get_object_or_404(Session, id=session_id)   

    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))    

    context = { 'form_title': _("Editing a session"),
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = SessionForm(data=request.POST, instance=session)
        if form.is_valid():
            form.save()  
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = SessionForm(instance=session)
        return render(request, 'Alpaca/_form_layout.html', context)


def confirm_session(request, activity_id):
    set_translation(request)
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        session = get_object_or_404(Session, id=request.POST.get("session_id"))
        session.confirm(user)

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


