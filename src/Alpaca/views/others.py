from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from ..models import Activity

def index(request):
    activity_list = Activity.objects.order_by('-pub_date')
    context = { 'user': request.user,
                'activity_list': activity_list }
    return render(request, 'Alpaca/index.html', context)


    