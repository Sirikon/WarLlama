from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile
from ..forms import ProfileCreationForm

from .utils import set_translation

import datetime

## -- AUTHENTICATION -- ##
def signup(request, activity_id):
    set_translation(request)
    if request.user.is_authenticated():
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))

    context = { 'submit_text': _("Sign up!"), 'rich_field_name': "" }

    if request.method == "POST":
        form = ProfileCreationForm(data=request.POST)

        if form.is_valid():
            form.save()
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_floating.html', context)
        
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))
    else:
        context['form'] = ProfileCreationForm()
        return render(request, 'Alpaca/_form_floating.html', context)


def login(request, activity_id):
    set_translation(request)
    if request.user.is_authenticated():
        if activity_id == "":
            return  HttpResponseRedirect(reverse('alpaca:index'))
        else:
            return  HttpResponseRedirect(reverse('alpaca:activity', kwargs={'activity_id': activity_id}))

    context = { 'submit_text': _("Log in"), 'rich_field_name': "" }

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
                context = {
                    'message_title': _('Error'),
                    'message_body': _('This user is not active at the moment. Please, verify your e-mail.')
                }
                return render(request, 'Alpaca/server_message.html', context)
        else:
            context['form'] = form
            return render(request, 'Alpaca/form_login.html', context)

    context['form'] = AuthenticationForm() 
    return render(request, 'Alpaca/form_login.html', context)

def logout(request):
    set_translation(request)
    auth.logout(request)
    return HttpResponseRedirect(reverse('alpaca:index'))