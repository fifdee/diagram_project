import datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_how_many_everyday_activities(value):
    print(f'value: {value}')
    if value < 1 or value > 50:
        print('raising')
        raise ValidationError('Podaj wartość od 1 do 50.')


def everyday_activity_conflicts(activity, everyday_activity_class):
    for current_activity in everyday_activity_class.objects.filter(subdivision=activity.subdivision):
        if activity.pk != current_activity.pk:
            if current_activity.name == activity.name:
                return True
    return None


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


def reordered_activities_count(activities_count):
    activities_count_new = {
        'Ewidencyjnie': activities_count['Ewidencyjnie'],
        'Obecni': activities_count['Obecni'],
        'Do zajęć': activities_count['Do zajęć'],
        'Służby': activities_count['Służby'],
        'Po służbie': activities_count['Po służbie'],
        'Urlopy': activities_count['Urlopy'],
        'L4': activities_count['L4'],
        'PS': activities_count['PS'],
        'Kursy': activities_count['Kursy'],
        'Poligon': activities_count['Poligon'],
    }
    return activities_count_new

def get_activities_count_for_day(day, subdivision):
    from diagram.models import Activity
    activities = {
        'Służby': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                          end_date__gte=day, name__in=[
                'SŁ.OF', 'SŁ.POM', 'SŁ.PDF', 'SŁ.DYŻ', 'SŁ.PST', 'SŁ.PKT', 'PA GAR', 'PA JW', 'OKO']).count(),
        'Po służbie': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                              end_date__gte=day, name__in=['PO SŁ.']).count(),
        'Urlopy': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                          end_date__gte=day, name__in= [
                'UR.WYP', 'WOLNE', 'UR.DOD', 'UR.OJC', 'UR.OK', 'UR.WYC', 'UR.SZK', 'HDK']).count(),
        'L4': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                              end_date__gte=day, name__in=['L4']).count(),
        'PS': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                      end_date__gte=day, name__in=['DYŻUR', 'PS']).count(),
        'Kursy': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                      end_date__gte=day, name__in=['KURS']).count(),
        'Poligon': Activity.objects.filter(subdivision=subdivision, start_date__lte=day,
                                                         end_date__gte=day, name__in=['POLIG']).count(),
    }

    return activities


def get_days_of_soldier_activity(soldier, activities_names, days_before):
    start_date = now().date() + datetime.timedelta(days=-days_before)
    end_date = now().date()
    days = 0
    for act in soldier.activity_set.filter(subdivision=soldier.subdivision, name__in=activities_names,
                                           start_date__lte=end_date, end_date__gte=start_date):
        measured_start_date = start_date
        if act.start_date > measured_start_date:
            measured_start_date = act.start_date

        measured_end_date = end_date
        if measured_end_date > act.end_date:
            measured_end_date = act.end_date

        days += (measured_end_date - measured_start_date).days + 1
    return days


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
                                             name=new_activity.name,
                                             description=new_activity.description)
    except Activity.DoesNotExist:
        print('No "left" activity for the same soldier and same activity name.')

    try:
        right_activity = Activity.objects.get(start_date=new_activity.end_date + datetime.timedelta(days=1),
                                              soldier=new_activity.soldier,
                                              name=new_activity.name,
                                              description=new_activity.description)
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


def assign_if_check_passed(new_instance):
    from diagram.models import Activity
    unassigned_activities = Activity.objects.filter(subdivision=new_instance.subdivision, soldier=None,
                                                    start_date=new_instance.start_date, end_date=new_instance.end_date,
                                                    name=new_instance.name)
    for unass_act in unassigned_activities:
        new_instance.description = unass_act.description
        unass_act.delete()


def update_soldier_info_names(subdivision, soldier_info_fields_names):
    from diagram.models import Soldier, SoldierInfo

    soldiers = Soldier.objects.filter(subdivision=subdivision)

    for soldier in soldiers:
        for prev_name, new_name in soldier_info_fields_names:
            try:
                soldier_info = SoldierInfo.objects.get(soldier=soldier, name=prev_name)
                soldier_info.name = new_name
                soldier_info.save()
            except SoldierInfo.DoesNotExist:
                f'There is no {prev_name} soldier info field name for {soldier}'


def unassigned_activities_as_string(unassigned_activities):
    output_string = ''
    i = 1
    if unassigned_activities.count() > 0:
        output_string += 'Nieprzypisane: '
    for act in unassigned_activities:
        if act.description != '':
            output_string += f'{i}. {act.name} ({act.description})'
        else:
            output_string += f'{i}. {act.name}'
        output_string += '; \n'
        i += 1
    return output_string


def everyday_activities_as_string(everyday_activities, this_day_activities):
    activities_to_assign = [{'name': act.name, 'count': act.how_many} for act in everyday_activities]

    for this_day_act in this_day_activities:
        for act_to_assign in activities_to_assign:
            if this_day_act.name == act_to_assign['name']:
                if act_to_assign['count'] > 1:
                    act_to_assign['count'] -= 1
                else:
                    activities_to_assign.remove(act_to_assign)

    output_string = ''
    i = 1
    if len(activities_to_assign) > 0:
        output_string += 'Codzienne aktywności do przypisania: '
    for act in activities_to_assign:
        output_string += f"{i}. {act['name']} x{act['count']}"
        output_string += '; \n'
        i += 1
    return output_string
