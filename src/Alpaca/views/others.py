from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.db.models import Count

from ..models import Activity

def index(request):
    to_sort_column = request.GET.get('order_by')
    sorted_column = request.GET.get('last')
    sort_sign = "-"
    
    if to_sort_column != None and to_sort_column != "":
        
        if sorted_column!= None and to_sort_column != "":
            if sorted_column[0] == "-":
                if to_sort_column == sorted_column[1:]:
                    sort_sign = ""
        
        if to_sort_column == "next_session":
            activity_list = sorted(Activity.objects.all(), key= lambda a: a.get_next_session().start_date, reverse=(sort_sign=="-"))

        elif to_sort_column == "attendants":
            activity_list = Activity.objects.annotate(num_attendants=Count('attendants')).order_by(sort_sign + 'num_attendants')

        else:
            activity_list = Activity.objects.order_by(sort_sign + to_sort_column)
    else: 
         activity_list = Activity.objects.order_by('-pub_date')
         to_sort_column = "pub_date"

    icon_name = "fa-sort-desc"
    if sort_sign == "-":
        icon_name = "fa-sort-asc"

    context = { 'user': request.user,
                'activity_list': activity_list,
                'sort_sign': sort_sign,
                'sorted_column': to_sort_column,
                'sort_icon': icon_name}

    return render(request, 'Alpaca/index.html', context)


    