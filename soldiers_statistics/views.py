from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic

from diagram.functions import get_days_of_soldier_activity
from diagram.models import Soldier


class StatisticsView(generic.View):
    def get(self, request):
        days_before = 90
        try:
            days_before = self.request.GET['days_before']
            if days_before == 'all':
                days_before = 9999
            else:
                days_before = int(days_before)
        except MultiValueDictKeyError:
            ...
        except ValueError:
            messages.add_message(self.request, messages.WARNING, f'Nieprawidłowa wartość parametru: {days_before}')
            return redirect('statistics')

        context = {
            'statistics': [{
                'pk': soldier.pk,
                'rank': soldier.rank,
                'first_name': soldier.first_name,
                'last_name': soldier.last_name,
                'L4': get_days_of_soldier_activity(soldier, ['L4'], days_before),
                'Dyżury': get_days_of_soldier_activity(soldier, ['DYŻUR'], days_before),
                'Służby': get_days_of_soldier_activity(soldier,
                                                       ['SŁ.OF', 'SŁ.POM', 'SŁ.PDF', 'SŁ.PST', 'SŁ.PKT', 'PA GAR',
                                                        'PA JW', 'OKO'], days_before),
                'HDK': get_days_of_soldier_activity(soldier, ['HDK'], days_before),
                'Urlopy': get_days_of_soldier_activity(soldier,
                                                       ['UR.WYP', 'WOLNE', 'UR.DOD', 'UR.OK', 'UR.WYC', 'UR.SZK'],
                                                       days_before),
                'Kursy': get_days_of_soldier_activity(soldier, ['KURS'], days_before),
            } for soldier in Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')]
        }

        return render(request, 'soldiers_statistics/statistics.html', context=context)
