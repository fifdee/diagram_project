def activity_conflicts(activity, activity_class):
    soldier = activity.soldier
    subdivision = soldier.subdivision

    other_activities = activity_class.objects.filter(subdivision=subdivision, soldier=soldier)
    print(other_activities)

    print('-------------------------------------')
    print(f'activity.start_date={activity.start_date}')
    print(f'activity.end_date={activity.end_date}')
    for iterated_activity in other_activities:
        if activity.pk != iterated_activity.pk:
            print(f'iterated_activity.start_date={iterated_activity.start_date}')
            print(f'iterated_activity.end_date={iterated_activity.end_date}')
            if (iterated_activity.start_date <= activity.start_date <= iterated_activity.end_date) or (
                    activity.start_date <= iterated_activity.start_date <= activity.end_date):
                return {'which_date': 'start_date', 'name': iterated_activity.name,
                        'start_date': iterated_activity.start_date, 'end_date': iterated_activity.end_date}
            if (iterated_activity.start_date <= activity.end_date <= iterated_activity.end_date) or (
                    activity.start_date <= iterated_activity.end_date <= activity.end_date):
                return {'which_date': 'end_date', 'name': iterated_activity.name,
                        'start_date': iterated_activity.start_date, 'end_date': iterated_activity.end_date}
            print('-------------------------------------')
    return None


def get_soldier_activities(activity_age, soldier):
    import datetime
    from django.utils.timezone import now
    from diagram.models import Activity

    activities = None
    if activity_age == '30days':
        activities = Activity.objects.filter(soldier=soldier,
                                             end_date__gte=now() - datetime.timedelta(days=30)).order_by('start_date')
    elif activity_age == '90days':
        activities = Activity.objects.filter(soldier=soldier,
                                             end_date__gte=now() - datetime.timedelta(days=90)).order_by('start_date')
    elif activity_age == '180days':
        activities = Activity.objects.filter(soldier=soldier,
                                             end_date__gte=now() - datetime.timedelta(days=180)).order_by('start_date')
    elif activity_age == 'all':
        activities = Activity.objects.filter(soldier=soldier).order_by('start_date')
    else:
        activities = Activity.objects.filter(soldier=soldier, end_date__gte=now()).order_by('start_date')
    return activities


def get_url_params(days_count_param, start_day_param):
    url_params = ''
    if days_count_param != '' or start_day_param != '':
        url_params += '?'
        if days_count_param != '':
            url_params += f'days_count={days_count_param}'
        if start_day_param != '':
            if days_count_param != '':
                url_params += f'&start_day={start_day_param}'
            else:
                url_params += f'start_day={start_day_param}'
    return url_params


def merge_neighbour_activities(new_activity):
    from diagram.models import Activity
    import datetime

    left_activity = None
    right_activity = None

    try:
        left_activity = Activity.objects.get(end_date=new_activity.start_date + datetime.timedelta(days=-1),
                                             soldier=new_activity.soldier,
                                             name=new_activity.name)
    except Activity.DoesNotExist:
        print('No "left" activity for the same soldier and same activity name.')

    try:
        right_activity = Activity.objects.get(start_date=new_activity.end_date + datetime.timedelta(days=1),
                                              soldier=new_activity.soldier,
                                              name=new_activity.name)
    except Activity.DoesNotExist:
        print('No "right" activity for the same soldier nad same activity name.')

    # MERGING THE SAME ACTIVITIES
    if left_activity and not right_activity:
        left_activity.end_date = new_activity.end_date
        new_activity.delete()
        left_activity.save()
    elif right_activity and not left_activity:
        right_activity.start_date = new_activity.start_date
        new_activity.delete()
        right_activity.save()
    elif left_activity and right_activity:
        left_activity.end_date = right_activity.end_date
        right_activity.delete()
        new_activity.delete()
        left_activity.save()