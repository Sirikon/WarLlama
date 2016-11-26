from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from settings import DEFAULT_FROM_EMAIL
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q


from django.utils import timezone
from django.views.generic import *

from .forms import *
from .models import *

import datetime

def index(request):
    activity_list = Activity.objects.order_by('-pub_date')
    context = { 'user': request.user,
                'activity_list': activity_list }
    return render(request, 'Alpaca/index.html', context)

## -- AUTHENTICATION -- ##
def signup(request, activity_id):
    if request.user.is_authenticated():
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))

    if request.method == "POST":
        form = ProfileCreationForm(data=request.POST)

        if form.is_valid():
            form.save()
        else:
            return render(request, 'Alpaca/signup.html', {'form': form})
        
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
    else:
        context = {'form': ProfileCreationForm()}
        return render(request, 'Alpaca/signup.html', context)


def login(request, activity_id):
    if request.user.is_authenticated():
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = request.POST['username']
            password = request.POST['password']
            access = auth.authenticate(username=user, password=password)
            if access is not None and access.is_active:
                auth.login(request, access)
                if activity_id == "":
                    return  HttpResponseRedirect(reverse('alpaca:index'))
                else:
                    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
            else:
                return render(request, 'Alpaca/not_active_user.html')
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/login.html', context)

    context = { 'form': AuthenticationForm() }
    return render(request, 'Alpaca/login.html', context)

def logout(request):

    auth.logout(request)
    return HttpResponseRedirect(reverse('alpaca:index'))
    

## -- USER MANAGEMENT -- ##
def reset_password(request):
    context = { 'form': form }
    return render(request, 'Alpaca/reset_password.html')

## -- ACTIVITIES -- ##
def new_activity(request):
    user = request.user
    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    if request.method == "POST":
        form = ActivityForm(data=request.POST)
        if form.is_valid():
            activity = form.save(commit=False)    
            activity.pub_date = timezone.now()
            activity.author = user
            activity.save()    
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/new_activity.html', context)

    else:
        context = {'form': ActivityForm()}
        return render(request, 'Alpaca/new_activity.html', context)


def edit_activity(request, activity_id):
    user = request.user
    activity = get_object_or_404(Activity, pk=activity_id)
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
                   
    if request.method == "POST":
        form = ActivityForm(data=request.POST, instance=activity)
        if form.is_valid():
            form.save()   
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/edit_activity.html', context)

    else:
        context = { 'form': ActivityForm(instance=activity) }
        return render(request, 'Alpaca/edit_activity.html', context)


def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user
    session_list = activity.session_set.order_by('start_date')
    context = { 'user': user,
                'activity': activity,
                'session_list': session_list}

    if user.is_authenticated:
        if user == activity.author:
            return render(request, 'Alpaca/activity_author.html', context)
        else:
            return render(request, 'Alpaca/activity_user.html', context)
    else:        
        return render(request, 'Alpaca/activity_anon.html', context)


def join_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        if activity.auto_register:
            activity.attendants.add(user)
        else:
            activity.pending_attendants.add(user)
        activity.save()
        # TO-DO --> Send "User has join your activity" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def leave_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user

    if request.method == "POST":
        activity.attendants.remove(user)
        activity.save()
        for session in activity.session_set.all():
            if not session.has_finished():
                session.confirmed_attendants.remove(user)
                session.save()
                # TO-DO --> Send "User has left your activity" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def kick_attendant(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("attending"))
        activity.attendants.remove(selected_user)
        activity.save()
        for session in activity.session_set.all():
            if not session.has_finished():
                session.confirmed_attendants.remove(selected_user)
                session.save()
                # TO-DO --> Send "You have been kicked from activity" email to kicked user

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


def pending_requests(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("request"))
        if "accept_request" in request.POST:
            activity.attendants.add(selected_user)
            activity.pending_attendants.remove(selected_user)

        elif "deny_request" in request.POST:
            activity.pending_attendants.remove(selected_user)            
        activity.save()
        # TO-DO --> Send "You have pending requests" email to activity's author

    return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))


## -- SESSIONS -- ##
def new_session(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    user = request.user
    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    if request.method == "POST":
        form = SessionForm(data=request.POST)
        if form.is_valid():
            session = form.save(commit=False)    
            session.activity = activity
            session.save()    
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/new_session.html', context)

    else:
        context = {'form': SessionForm()}
        return render(request, 'Alpaca/new_session.html', context)


def edit_session(request, activity_id, session_id):
    user = request.user
    activity = get_object_or_404(Activity, id=activity_id)   
    session = get_object_or_404(Session, id=session_id)   

    if not user.is_authenticated() or user != activity.author:
        return  HttpResponseRedirect(reverse('alpaca:index'))    

    if request.method == "POST":
        form = SessionForm(data=request.POST, instance=session)
        if form.is_valid():
            form.save()   
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity.id}))
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/edit_session.html', context)

    else:
        context = {'form': SessionForm(instance=session)}
        return render(request, 'Alpaca/edit_session.html', context)


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


