from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Activity

from utils import sort_activity_table, set_translation


def index(request):
    set_translation(request)
    user = request.user
    user_filter = request.GET.get('filter')
    to_sort_column = request.GET.get('order_by')
    last_column = request.GET.get('last')
    
    activity_list = Activity.objects
    if user_filter == "author":
        activity_list = activity_list.filter(author__id=user.id)
    elif user_filter == "attendant":
        activity_list = user.attending_activities

    context = sort_activity_table(activity_list, to_sort_column, last_column)
    context['user'] = user

    return render(request, 'Alpaca/index.html', context)

def activity_summary_demo(request):
    set_translation(request)
    user = request.user
    user_filter = request.GET.get('filter')
    to_sort_column = request.GET.get('order_by')
    last_column = request.GET.get('last')
    
    activity_list = Activity.objects
    if user_filter == "author":
        activity_list = activity_list.filter(author__id=user.id)
    elif user_filter == "attendant":
        activity_list = user.attending_activities

    context = sort_activity_table(activity_list, to_sort_column, last_column)
    context['user'] = user
   
    return render(request, 'Alpaca/index_demo.html', context)