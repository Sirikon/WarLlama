from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from django.views.generic import *
from django.contrib.auth.models import User

from ..models import Profile

## -- USER MANAGEMENT -- ##
def reset_password(request):
    context = { 'submit_text': "Sign up!", 
                'rich_field_name': "",
                'form': None }
    return render(request, 'Alpaca/form_floating.html')
