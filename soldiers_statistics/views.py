from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic

from diagram.functions import get_days_of_soldier_activity
from diagram.models import Soldier


class StatisticsView(LoginRequiredMixin, generic.View):
    def get(self, request):
        days_before_param = request.GET.get('days_before', None)
        if days_before_param and days_before_param in ['30', '90', '180', 'all']:
            if days_before_param == 'all':
                days_before_param = 9999
            else:
                days_before_param = int(days_before_param)
            request.session['days_before'] = days_before_param
        days_before = request.session.get('days_before', 90)

        order_key_param = request.GET.get('order_key', None)
        if order_key_param and order_key_param in ['last_name', 'L4', 'Dyżury', 'Służby', 'HDK', 'Urlopy', 'Kursy',
                                                   'PS', 'Poligony']:
            request.session['order_key'] = order_key_param
        order_key = request.session.get('order_key', 'last_name')

        content = [{
            'pk': soldier.pk,
            'rank': soldier.rank,
            'first_name': soldier.first_name,
            'last_name': soldier.last_name,
            'L4': get_days_of_soldier_activity(soldier, ['L4'], days_before),
            'Dyżury': get_days_of_soldier_activity(soldier, ['DYŻUR'], days_before),
            'Służby': get_days_of_soldier_activity(soldier,
                                                   ['SŁ.OF', 'SŁ.POM', 'SŁ.PDF', 'SŁ.DYŻ', 'SŁ.PST', 'SŁ.PKT', 'PA GAR',
                                                    'PA JW', 'OKO'], days_before),
            'HDK': get_days_of_soldier_activity(soldier, ['HDK'], days_before),
            'Urlopy': get_days_of_soldier_activity(soldier,
                                                   ['UR.WYP', 'WOLNE', 'UR.DOD', 'UR.OK', 'UR.OJC', 'UR.WYC', 'UR.SZK'],
                                                   days_before),
            'Kursy': get_days_of_soldier_activity(soldier, ['KURS'], days_before),
            'PS': get_days_of_soldier_activity(soldier, ['PS'], days_before),
            'Poligony': get_days_of_soldier_activity(soldier, ['POLIG'], days_before),
        } for soldier in Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')
        ]

        return render(request, 'soldiers_statistics/statistics.html',
                      context={'statistics': sorted(content, key=lambda x: x[order_key])})
