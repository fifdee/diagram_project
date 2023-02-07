import datetime

from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from diagram.models import Soldier


class StatisticsView(generic.View):
    def get(self, request):
        context = {
            'statistics': [{
                'pk': soldier.pk,
                'rank': soldier.rank,
                'first_name': soldier.first_name,
                'last_name': soldier.last_name,
                'L4': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    subdivision=request.user.subdivision, name='L4')]),
                'Dyżury': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    subdivision=request.user.subdivision, name='DYŻUR')]),
                'Służby': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    Q(subdivision=request.user.subdivision, name='SŁ.OF') |
                    Q(subdivision=request.user.subdivision, name='SŁ.POM') |
                    Q(subdivision=request.user.subdivision, name='SŁ.PDF') |
                    Q(subdivision=request.user.subdivision, name='SŁ.PST') |
                    Q(subdivision=request.user.subdivision, name='SŁ.PKT') |
                    Q(subdivision=request.user.subdivision, name='PA GAR') |
                    Q(subdivision=request.user.subdivision, name='PA JW') |
                    Q(subdivision=request.user.subdivision, name='OKO')
                )]),
                'HDK': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    subdivision=request.user.subdivision, name='HDK')]),
                'Urlopy': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    Q(subdivision=request.user.subdivision, name='UR.WYP') |
                    Q(subdivision=request.user.subdivision, name='WOLNE') |
                    Q(subdivision=request.user.subdivision, name='UR.DOD') |
                    Q(subdivision=request.user.subdivision, name='UR.OK') |
                    Q(subdivision=request.user.subdivision, name='UR.WYC') |
                    Q(subdivision=request.user.subdivision, name='UR.SZK')
                )]),
                'Kursy': sum([(act.end_date - act.start_date).days + 1 for act in soldier.activity_set.filter(
                    subdivision=request.user.subdivision, name='KURS')]),
            } for soldier in Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')]
        }

        return render(request, 'soldiers_statistics/statistics.html', context=context)