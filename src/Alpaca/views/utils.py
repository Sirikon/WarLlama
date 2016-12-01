from django.db.models import Count, Q

# Useful functions for the views. These functions return contexts.

def sort_activity_table(activity_list, sort_column, last_column):
    sort_sign = "-"

    if sort_column != None and sort_column != "":        
        if last_column != None and sort_column != "":
            if last_column[0] == "-":
                if sort_column == last_column[1:]:
                    sort_sign = ""
        
        if sort_column == "next_session":
            sorted_list = sorted(activity_list.all(), key= lambda a: a.get_next_session().start_date, reverse=(sort_sign=="-"))

        elif sort_column == "attendants":
            sorted_list = activity_list.annotate(num_attendants=Count('attendants')).order_by(sort_sign + 'num_attendants')

        else:
            sorted_list = activity_list.order_by(sort_sign + sort_column)
    else: 
         sorted_list = activity_list.order_by('-pub_date')
         sort_column = "pub_date"
    
    icon_name = "fa-sort-desc"
    if sort_sign == "-":
        icon_name = "fa-sort-asc"

    context = { 'activity_list': sorted_list,
                'sort_sign': sort_sign,
                'sorted_column': sort_column,
                'sort_icon': icon_name }

    return context