from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

# Create your views here.
def index(request):
    activity_list = Activity.objects.order_by('-pub_date')
    context = {'activity_list': activity_list }
    return render(request, 'Alpaca/index.html', context)

def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    session_list = activity.session_set.order_by('-start_date')
    context = {'activity': activity,
               'session_list': session_list}
    return render(request, 'Alpaca/activity.html', context)


def signup(request):
    if request.method == "POST":
        form = ProfileCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
        text = "Welcome to Alpaca!"
        return  HttpResponseRedirect(reverse('alpaca:index'))
    else:
        context = {'form': ProfileCreationForm()}
        return render(request, 'Alpaca/signup.html', context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = request.POST['username']
            password = request.POST['password']
            access = authenticate(username=user, password=password)
            if access is not None and access.is_active:
                auth_login(request, access)
                return HttpResponseRedirect(reverse('alpaca:index'))
            else:
                return render(request, 'Alpaca/not_active_user.html')
        else:
            context = { 'form': form }
            return render(request, 'Alpaca/login.html', context)

    context = { 'form': AuthenticationForm() }
    return render(request, 'Alpaca/login.html', context)