from django.shortcuts import render
from django.utils.timezone import now
from django.views import generic
import datetime

from diagram.models import Soldier, Activity


class ShowDiagram(generic.View):
    def get(self, request):
        today = now()
        soldiers = Soldier.objects.filter(subdivision=request.user.subdivision)
        activities = {}

        for soldier in soldiers:
            activities[soldier] = {}
            for j in range(0, 16):
                this_date = today + datetime.timedelta(days=j)
                activities[soldier][j] = '0'
                try:
                    activity = Activity.objects.get(soldier=soldier, start_date__gte=this_date,
                                                    end_date__lte=this_date)
                    activities[soldier][j] = f'{activity.name} {activity.description}'
                except Activity.DoesNotExist:
                    pass

        context = {
            'activities': activities
        }

        return render(request, template_name='diagram/show_diagram.html', context=context)
