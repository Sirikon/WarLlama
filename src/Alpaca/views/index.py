from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from itertools import chain

from Alpaca.models.activity_model import Activity
from ..forms import *

from ..utils import *


def index(request):
    set_translation(request)
    user = request.user
    user_filter = request.GET.get('filter')
    to_sort_column = request.GET.get('order_by')
    last_column = request.GET.get('last')

    activity_list = search(request, "search", [Activity], ['title', 'age_minimum', 'author__username', 'city', 'description'])   
    activity_list = filter_activities(request, user, user_filter, activity_list)

    if activity_list is None:
        #activity_list = list(chain(Activity.objects.all(), Event.objects.all()))
        activity_list = list(Activity.objects.all())
        
    form = DateRangeFilterForm()
    #if "date_range_filter" in request.POST:
    #    form = DateRangeFilterForm(data=request.POST)
    #    if form.is_valid():
    #        activity_list = form.get_activities(activity_list)

    context = sort_activities(activity_list, to_sort_column, last_column)   
    context["current_filter"] = user_filter
    context['user'] = user

    context['form'] = form
    context['form_title'] = _("Next Session")
    context['form_name'] = "date_range_filter"
    context['submit_text'] = _("Show")

    return render(request, 'Alpaca/index.html', context)

def group_index(request):
    set_translation(request)
    user = request.user

    user_filter = request.GET.get('filter')

    group_list = search(request, "search", Group, ['name', 'description', 'email'])    
    group_list = filter_groups(request, user, user_filter, group_list)
    
    if group_list is None:
        group_list = list(Group.objects.all())
    
    context = {
        "user": user,
        "current_filter": user_filter,
        "group_list": group_list
    }
    return render(request, 'Alpaca/group/_group_index.html', context)


def about_us(request):
    set_translation(request)
    return render(request, 'Alpaca/about_us.html')


def terms_conditions(request):
    set_translation(request)
    return render(request, 'Alpaca/terms_conditions.html')

