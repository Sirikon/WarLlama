from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile, Activity
from ..forms import ProfileForm, ChangePasswordForm

from utils import sort_activities, set_translation

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
                
    return render(request, 'Alpaca/user_profile.html', context)

def edit_profile(request):
    set_translation(request)
    user = request.user

    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Edit your profile's settings"),
                'submit_text': _("Save changes"),
                'rich_field_name': "" }

    if request.method == "POST":
        form = ProfileForm(data=request.POST, instance=user.profile)
        if form.is_valid():
            form.save()   
            return  HttpResponseRedirect(reverse('alpaca:profile', kwargs={'username': user.username}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/form_edit_profile.html', context)

    else:
        context['form'] = ProfileForm(instance=user.profile)
        return render(request, 'Alpaca/form_edit_profile.html', context)

def reset_password(request):
    set_translation(request)
    context = { 'submit_text': _("Sign up!"), 
                'rich_field_name': "",
                'form': None }
    return render(request, 'Alpaca/form_floating.html')

def change_password(request):
    set_translation(request)
    user = request.user

    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))

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
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = ChangePasswordForm()
        return render(request, 'Alpaca/_form_layout.html', context)