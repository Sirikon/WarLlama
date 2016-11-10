from django.shortcuts import render, get_object_or_404

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
