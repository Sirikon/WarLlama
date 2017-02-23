from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.contrib import auth
from django.views.generic import *
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile, Activity
from ..forms import *
from ..emails import *

from ..utils import sort_activities, set_translation

import datetime



## -- AUTHENTICATION -- ##
def signup(request):
    set_translation(request)

    if request.user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

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
            return render(request, 'Alpaca/signup/signup.html', context)
        
    else:
        context['form'] = ProfileCreationForm()
        return render(request, 'Alpaca/signup/signup.html', context)


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


def login(request):
    set_translation(request)
    if request.user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'submit_text': _("Log in"), 'rich_field_name': "" }

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = request.POST['username']
            password = request.POST['password']
            access = auth.authenticate(username=user, password=password)
            if access is not None and access.is_active:
                auth.login(request, access)
                return  HttpResponseRedirect(reverse('alpaca:index'))
            else:
                context = {
                    'message_title': _('Error'),
                    'message_body': _('This user is not active at the moment. Please, verify your e-mail.')
                }
                return render(request, 'Alpaca/server_message.html', context)
        else:
            context['form'] = form
            return render(request, 'Alpaca/login/login.html', context)

    context['form'] = AuthenticationForm() 
    return render(request, 'Alpaca/login/login.html', context)

def logout(request):
    set_translation(request)
    auth.logout(request)
    return HttpResponseRedirect(reverse('alpaca:index'))

## -- PASSWORD MANAGEMENT -- ##
def forgot_password(request):
    set_translation(request)
    user = request.user

    if user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Ask for a new password"),
                'submit_text': _("Submit"),
                'rich_field_name': "" }

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            submitted = form.cleaned_data["email_or_username"]
            user = get_object_or_404(User, Q(username=submitted) | Q(email=submitted))

            user.profile.generate_token()
            
            email_reset_password(user)

            context = {
                'message_title': _("Check your inbox!"),
                'message_body': _("We have sent you an e-email that will help you get a new password.")
            }            
            return render(request, 'Alpaca/server_message.html', context)

        else:
            context['form'] = form
            return render(request, 'Alpaca/shared/layouts/_form-floating-layout.html', context)

    context['form'] = ForgotPasswordForm()
    return render(request, 'Alpaca/shared/layouts/_form-floating-layout.html', context)

def reset_password(request):
    set_translation(request)

    if request.user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))
     
    email = request.GET.get('email')
    token = request.GET.get('token')
    
    user = get_object_or_404(User, email=email)

    context = { 'form_title': _("Change your password"),
                'submit_text': _("Save"),
                'rich_field_name': "" }
    if user.profile.current_token == token:
        if request.method == "POST":
            form = NewPasswordForm(request.POST)
            if form.is_valid(user):
                form.save(user)   
                context = {
                    'message_title': _("Great!"),
                    'message_body': _("Your new password is in place. Use it now to log in!")
                }            
                return render(request, 'Alpaca/server-message/server-message.html', context)

            else:
                context['form'] = form
                return render(request, 'shared/layouts/_form-floating-layout.html', context)
        else:
            context['form'] = NewPasswordForm()
            return render(request, 'shared/layouts/_form-floating-layout.html', context)
        
    context['message_title'] = _('What are you doing here?')
    context['message_body'] = _('It seems like you got lost in our page. Click the Alpaca logo to go back to the index.')

    return render(request, 'Alpaca/server-message/server-message.html', context)


@login_required
def change_password(request):
    set_translation(request)
    user = request.user

    context = { 'form_title': _("Change your password"),
                'submit_text': _("Save new password"),
                'rich_field_name': "" }

    if request.method == "POST":
        form = ChangePasswordForm(data=request.POST)
        if form.is_valid(user):
            form.save(user)   
            return  HttpResponseRedirect(reverse('alpaca:profile', kwargs={'username': user.username}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/shared/layouts/_form-layout.html', context)

    else:
        context['form'] = ChangePasswordForm()
        return render(request, 'Alpaca/shared/layouts/_form-layout.html', context)


## -- USER MANAGEMENT -- ##
def profile(request, username):
    set_translation(request)
    user = request.user
    looking_at_user = get_object_or_404(User, username=username)
    to_sort_column = request.GET.get('order_by')
    sorted_column = request.GET.get('last')

    context = sort_activities(Activity.objects.filter(author_id=looking_at_user.id), to_sort_column, sorted_column)

    context['user'] = request.user
    context['looking_at_user'] = looking_at_user
                
    return render(request, 'Alpaca/user-profile/user-profile.html', context)

@login_required
def edit_profile(request):
    set_translation(request)
    user = request.user

    context = { 'form_title': _("Edit your profile's settings"),
                'submit_text': _("Save changes"),
                'rich_field_name': "" }

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile = form.save()
            return  HttpResponseRedirect(reverse('alpaca:profile', kwargs={'username': user.username}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/user-profile/form-edit-profile.html', context)

    else:
        context['form'] = ProfileForm(instance=user)
        return render(request, 'Alpaca/user-profile/form-edit-profile.html', context)


