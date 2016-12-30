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

from .utils import set_translation, generate_token
from .emails import *

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
            new_user = form.save()
            new_user.profile.generate_token()
                        
            email_confirm_account(new_user)

            context = {
                'message_title': _('You are signed up!'),
                'message_body': _('Your user is not active at the moment. Please, verify your e-mail (it could end up in the spam folder).')
            }
            
            return render(request, 'Alpaca/server_message.html', context)
            
        else:
            context['form'] = form
            return render(request, 'Alpaca/form_signup.html', context)
        
    else:
        context['form'] = ProfileCreationForm()
        return render(request, 'Alpaca/form_signup.html', context)


def activate(request):
    set_translation(request)

    if request.user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

    email = request.GET.get('email')
    token = request.GET.get('token')

    user = get_object_or_404(User, email=email)

    context = {}
    if user.profile.current_token == token:
        user.profile.activate()

        context['message_title'] = _('Welcome to Alpaca!')
        context['message_body'] = _('You are one of us now. Your account has been activated and you may now log in. Welcome!')
    else:
        context['message_title'] = _('What are you doing here?')
        context['message_body'] = _('It seems like you got lost in our page. Click the Alpaca logo to go back to the index.')

    return render(request, 'Alpaca/server_message.html', context)


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