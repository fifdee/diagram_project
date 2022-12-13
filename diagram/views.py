from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views import generic
import datetime

from diagram.models import Soldier, Activity
from diagram.text_choices import activity_names


class ShowDiagram(generic.View):
    def get(self, request):
        today = now().date()
        soldiers = Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')
        activities = {}
        dates = set()

        for soldier in soldiers:
            activities[soldier] = {}
            for j in range(0, 16):
                this_date = today + datetime.timedelta(days=j)
                dates.add(this_date)
                activities[soldier][j] = {}
                activities[soldier][j]['name'] = ''
                activities[soldier][j]['date'] = this_date.strftime('%d.%m.%Y')
                activities[soldier][j]['soldier_pk'] = soldier.pk

                try:
                    activity = Activity.objects.get(soldier=soldier, start_date__lte=this_date,
                                                    end_date__gte=this_date)
                    activities[soldier][j]['name'] = activity
                    activities[soldier][j]['pk'] = activity.pk
                except Activity.DoesNotExist:
                    pass

        context = {
            'activities': activities,
            'dates': sorted(dates),
            'choices': sorted(activity_names),
        }

        return render(request, template_name='diagram/show_diagram.html', context=context)

    def post(self, request):
        soldier = Soldier.objects.get(pk=request.POST['soldier_pk'])
        activity_name = request.POST['activity_new']
        day = datetime.datetime.strptime(request.POST['date'], '%d.%m.%Y')

        print(soldier)
        print(activity_name)
        print(day)

        activity_previous_pk = request.POST['activity_previous_pk']
        if activity_previous_pk != '':
            previous_activity = Activity.objects.get(pk=activity_previous_pk)
        #     TODO usunąć poprzednią aktywność w tym dniu lub rozbić na dwie jeśli daty są szersze

        Activity.objects.create(
            soldier=soldier,
            name=activity_name,
            start_date=day,
            end_date=day
        )

        # TODO sprawdzić czy są aktywności okalające z lewej i / lub prawej i w razie konieczności jeśli jest taka sama - połączyć
        return redirect('show-diagram')
