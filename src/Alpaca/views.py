from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

# Create your views here.
def index(request):
    activity_list = Activity.objects.order_by('-pub_date')
    context = { 'user': request.user,
                'activity_list': activity_list }
    return render(request, 'Alpaca/index.html', context)

def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    user = request.user
    authenticated = user.is_authenticated()

    if request.method == "POST" and authenticated:
        if "al_join" in request.POST:
            activity.attendants.add(user)
            activity.save()
            
        if  "al_confirm" in request.POST:
            if user in activity.attendants:
                session = get_object_or_404(Session, request.POST.get("session_id"))
                if activity == session.activity and session.isOnConfirmationPeriod():
                    session.confirmed_attendants.add(user)
                    session.save()

    session_list = activity.session_set.order_by('-start_date')
# authenticated and s.isOnConfirmationPeriod() and s.canUserJoin(user)
    context = { 'user': user,
                'activity': activity,
                'session_list': session_list }

    return render(request, 'Alpaca/activity.html', context)


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
    