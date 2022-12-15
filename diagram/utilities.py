from diagram.models import Activity


def activity_conflicts(activity):
    subdivision = activity.subdivision
    soldier = activity.soldier

    other_activities = Activity.objects.filter(subdivision=subdivision, soldier=soldier)
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
