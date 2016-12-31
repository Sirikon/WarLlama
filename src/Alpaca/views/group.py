from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile, Group, Activity
from ..forms import GroupForm
from ..emails import email_reset_password
from ..utils import set_translation

import datetime


def group(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)
    user = request.user
    activity_list = group.activity_list.order_by('pub_date')
    context = { 'user': user,
                'group': group,
                'activity_list': activity_list}

    if user.is_authenticated:
        if user == group.superuser or user in group.admin_list.all():
            return render(request, 'Alpaca/group/group_admin.html', context)
        else:
            return render(request, 'Alpaca/group/group_member.html', context)
    else:        
        return render(request, 'Alpaca/group/group_anon.html', context)

def new_group(request):
    set_translation(request)
    
    user = request.user
    if not user.is_authenticated():
        return  HttpResponseRedirect(reverse('alpaca:index'))
    
    context = { 'form_title': _("Start a new group!"),
                'submit_text': _("Create!"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)    
            logo = form.cleaned_data["logo"]
            group.new(timezone.now(), user, logo)

            return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = GroupForm() 
        return render(request, 'Alpaca/_form_layout.html', context)


def edit_group(request, group_id):
    set_translation(request)
    user = request.user
    group = get_object_or_404(Group, pk=group_id)
    if not user.is_authenticated() or (user != group.superuser and user not in group.admin_list.all()):
        return  HttpResponseRedirect(reverse('alpaca:index'))

    context = { 'form_title': _("Editing group") + " " + group.name,
                'submit_text': _("Save changes"),
                'rich_field_name': "description" }

    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group = form.save(commit=False)   
            group.edit(form.cleaned_data["logo"])
            
            return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group.id}))
        else:
            context['form'] = form
            return render(request, 'Alpaca/_form_layout.html', context)

    else:
        context['form'] = GroupForm(instance=group)
        return render(request, 'Alpaca/_form_layout.html', context)


## USER ACTIONS ##
def join_group(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)
    user = request.user

    if request.method == "POST":
        group,join(user)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))


def leave_group(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)
    user = request.user

    if request.method == "POST":
        group.leave(user)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

## ADMIN ACTIONS ##
def handle_member(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("member"))
        if "promote_member" in request.POST:
            group.promote(selected_user)
        elif "kick_member" in request.POST: 
            group.kick(selected_user)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

def pending_members(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        group.handle_user_request(selected_user, "accept_request" in request.POST)
        
    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

def pending_activities(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_activity = get_object_or_404(Activity, id=request.POST.get("activity_request"))
        group.handle_activity_request(selected_activity, "accept_request" in request.POST)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

def demote_admin(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("member"))
        group.demote(selected_user)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))
