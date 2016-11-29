from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ..models import Profile, Activity

from utils import sort_activity_table

## -- USER MANAGEMENT -- ##
def reset_password(request):
    context = { 'submit_text': "Sign up!", 
                'rich_field_name': "",
                'form': None }
    return render(request, 'Alpaca/form_floating.html')

def profile(request, username):
    user = request.user
    looking_at_user = get_object_or_404(User, username=username)
    complete_name = ""
    if looking_at_user.first_name != "":
        complete_name = looking_at_user.first_name
        if looking_at_user.last_name != "":
            complete_name += " " + looking_at_user.last_name
    elif looking_at_user.last_name != "":
        complete_name = looking_at_user.last_name
        
    to_sort_column = request.GET.get('order_by')
    sorted_column = request.GET.get('last')

    context = sort_activity_table(Activity.objects.filter(author_id=looking_at_user.id), to_sort_column, sorted_column)

    context['user'] = request.user
    context['looking_at_user'] = looking_at_user
    context['complete_name'] = complete_name 
                
    return render(request, 'Alpaca/user_profile.html', context)
