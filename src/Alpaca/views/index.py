from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from ..models import Activity, activity_no_cover_path
from ..forms import *

from utils import *


def index(request):
    set_translation(request)
    user = request.user
    user_filter = request.GET.get('filter')
    to_sort_column = request.GET.get('order_by')
    last_column = request.GET.get('last')

    activity_list = search(request, "search", Activity, ['title', 'age_minimum', 'author__username', 'city', 'description'])    
    
    if activity_list is None:
        activity_list = Activity.objects

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


def index_demo(request):
    set_translation(request)
    user = request.user

    form = DateRangeFilterForm()
    activity_list = None

    # Search is available to anons
    activity_list = search(request, "search", Activity, ['title', 'age_minimum', 'author__username', 'city', 'description'])    
    
    if "date_range_filter" in request.GET:
        form = DateRangeFilterForm(data=request.GET)
        if form.is_valid():
            activity_list = form.get_activities()

    if activity_list is None:
        activity_list = Activity.objects

    user_filter = request.GET.get('filter')
    to_sort_column = request.GET.get('order_by')
    last_column = request.GET.get('last')

    if user.is_authenticated: # Can't filter for anons
        if user_filter == "author":
            activity_list = activity_list.filter(author__id=user.id)
        elif user_filter == "attendant":
            activity_list = user.attending_activities    

    context = sort_activities(activity_list, to_sort_column, last_column)
    context["current_filter"] = user_filter
    context['user'] = user

    context['form'] = form
    context['form_title'] = _("Next Session")
    context['form_name'] = "date_range_filter"
    context['submit_text'] = _("Show")

    return render(request, 'Alpaca/index_demo.html', context)