from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Profile, Group, Activity
from ..forms import GroupForm
from .emails import email_reset_password

from utils import set_translation

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
            group.creation_date = timezone.now()
            group.superuser = user
            group.total_num_members = 1
            group.logo = form.cleaned_data["logo"]
            group.save()  
            #email_registered_your_new_activity(activity)  
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
            group.logo = form.cleaned_data["logo"]
            group.save() 
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
        if group.auto_register_users:
            group.member_list.add(user)
            group.total_num_members = group.member_count()
            #email_user_acted_on_your_activity(group, user, True)
        else:
            group.pending_members.add(user)
            #email_user_requested_to_join(group, user)
        group.save()

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))


def leave_group(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)
    user = request.user

    if request.method == "POST":
        group.members.remove(user)
        group.total_num_members = group.member_count()
        group.save()
        #email_user_acted_on_your_activity(group, user, False)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

## ADMIN ACTIONS ##
def handle_member(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("member"))
        if "promote_member" in request.POST:
            group.admin_list.add(selected_user)
            group.member_list.remove(selected_user)
            #email_you_were_kicked_out_from_activity(activity, selected_user)   
        elif "kick_member" in request.POST: 
            group.member_list.remove(selected_user)
            group.total_num_members = group.member_count()
            #email_you_were_kicked_out_from_activity(activity, selected_user)
        group.save()

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

def pending_members(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("user_join_request"))
        if "accept_request" in request.POST:
            group.member_list.add(selected_user)
            group.pending_members.remove(selected_user)
            #email_your_request_was_handled(group, selected_user, True)

        elif "reject_request" in request.POST:
            group.pending_members.remove(selected_user)   
            #email_your_request_was_handled(group, selected_user, False)
        
        group.total_num_members = group.member_count()
        group.save()

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))

def pending_activities(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_activity = get_object_or_404(Activity, id=request.POST.get("activity_request"))
        if "accept_request" in request.POST:
            selected_activity.pending_group = None
            selected_activity.group = group
            #TO-DO: email_your_request_was_handled(group, selected_user, True)

        elif "reject_request" in request.POST:
            selected_activity.pending_group = None  
            #TO-DO: email_your_request_was_handled(group, selected_user, False)
        selected_activity.save()

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))



def demote_admin(request, group_id):
    set_translation(request)
    group = get_object_or_404(Group, pk=group_id)

    if request.method == "POST":
        selected_user = get_object_or_404(User, id=request.POST.get("member"))
        group.admin_list.remove(selected_user)
        group.member_list.add(selected_user)
        group.save()
        #email_you_were_kicked_out_from_activity(activity, selected_user)

    return  HttpResponseRedirect(reverse('alpaca:group', kwargs={'group_id': group_id}))
