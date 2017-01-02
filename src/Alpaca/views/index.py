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

    activity_list = search(request, "search", [Activity, Event], ['title', 'age_minimum', 'author__username', 'city', 'description'])    
    
    if activity_list is None:
        activity_list = list(chain(Activity.objects.all(), Event.objects.all()))

    activity_list = filter_activities(request, user, activity_list, user_filter)
    context = sort_activities(activity_list, to_sort_column, last_column)
    
    form = DateRangeFilterForm()
    if "date_range_filter" in request.POST:
        form = DateRangeFilterForm(data=request.POST)
        if form.is_valid():
            context['activity_list'] = form.get_activities(context['activity_list'])

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
    
    if group_list is None:
        group_list = Group.objects

    group_list = filter_groups(request, user, group_list, user_filter)
    
    context = {
        "user": user,
        "current_filter": user_filter,
        "group_list": group_list.all()
    }
    return render(request, 'Alpaca/group/_group_index.html', context)


def about_us(request):
    set_translation(request)
    return render(request, 'Alpaca/about_us.html')


def terms_conditions(request):
    set_translation(request)
    return render(request, 'Alpaca/terms_conditions.html')

