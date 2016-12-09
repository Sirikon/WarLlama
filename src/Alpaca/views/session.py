from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language
from django.core.mail import EmailMessage

from ..models import Activity, Session
from ..forms import SessionForm

from .utils import set_translation

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
            session.activity = activity
            session.save()    
            
            # Send "New Session" email to all attendants
            for att in activity.attendants.all():
                msg = EmailMessage("New Session in Activity " + activity.title, 
                            "Hi," +
                            "<br><br>You are receiving this message because the activity " + activity.title + " was updated with new sessions!" +
                            "<br><br>Check them out at http://alpaca.srk.bz/activity/" + str(activity.id) + "! Hope to see you there <3" +
                            "<br><br>Alpaca hugs, always watching over you," +
                            "<br>Big Evil Llama", 
                            'noreply@alpaca.srk.bz', 
                            [att.email])
                msg.content_subtype = "html"
                msg.send()

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
        if user in activity.attendants.all():
            session = get_object_or_404(Session, id=request.POST.get("session_id"))
            if activity == session.activity and session.is_on_confirmation_period():
                session.confirmed_attendants.add(user)
                session.save()
                # Send "User has confirmed assistance" email to activity's author
                msg = EmailMessage("Update on your activity " + activity.title + " - " + user.username + " confirmed assistance", 
                          "Hi, " + activity.author.username + 
                            "<br><br>Congratulations! " + user.username + " has confirmed assistance to the " + session.datetime.date +"'s session!'" +
                            "<br><br>I hope everything goes as your expect it <3" +
                            "<br><br>Alpaca hugs, always watching over you," +
                            "<br>Big Evil Llama", 
                          'noreply@alpaca.srk.bz', 
                          [activity.author.email])
                msg.content_subtype = "html"
                msg.send()

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


