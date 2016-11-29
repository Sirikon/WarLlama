from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.db.models import Count

from ..models import Activity

from utils import sort_activity_table


def index(request):
    to_sort_column = request.GET.get('order_by')
    sorted_column = request.GET.get('last')
    
    context = sort_activity_table(Activity.objects, to_sort_column, sorted_column)
    context['user'] = request.user

    return render(request, 'Alpaca/index.html', context)


    