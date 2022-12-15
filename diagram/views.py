from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views import generic
import datetime

from diagram.forms import SoldierForm, ActivityForm
from diagram.models import Soldier, Activity
from diagram.text_choices import activity_names


class ShowDiagram(LoginRequiredMixin, generic.View):
    def get(self, request):
        today = now().date()
        soldiers = Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')
        activities = {}
        dates = set()

        for soldier in soldiers:
            activities[soldier] = {}
            for j in range(0, 14):
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
            'choices': sorted([a[0] for a in activity_names]),
        }

        return render(request, template_name='diagram/show_diagram.html', context=context)

    def post(self, request):
        soldier = Soldier.objects.get(pk=request.POST['soldier_pk'])
        activity_name = request.POST['activity_new']
        day = datetime.datetime.strptime(request.POST['date'], '%d.%m.%Y').date()

        print(soldier)
        print(activity_name)
        print(day)

        activity_previous_pk = request.POST['activity_previous_pk']
        if activity_previous_pk != '':
            # MODIFYING OR SPLITTING PREVIOUS ACTIVITY
            previous_activity = Activity.objects.get(pk=activity_previous_pk)
            print(f'previous_activity.start_date: {previous_activity.start_date}')
            print(f'previous_activity.end_date: {previous_activity.end_date}')

            if previous_activity.start_date == day and previous_activity.end_date == day:
                previous_activity.delete()
            elif previous_activity.start_date < day and previous_activity.end_date == day:
                previous_activity.end_date = previous_activity.end_date + datetime.timedelta(days=-1)
                previous_activity.save()
            elif previous_activity.start_date == day and previous_activity.end_date > day:
                previous_activity.start_date = previous_activity.start_date + datetime.timedelta(days=1)
                previous_activity.save()
            else:
                end_date = previous_activity.end_date
                previous_activity.end_date = day + datetime.timedelta(days=-1)
                previous_activity.save()

                Activity.objects.create(
                    soldier=previous_activity.soldier,
                    name=previous_activity.name,
                    description=previous_activity.description,
                    start_date=day + datetime.timedelta(days=1),
                    end_date=end_date,
                    subdivision=request.user.subdivision
                )

        new_activity = None
        if activity_name != '':
            new_activity = Activity.objects.create(
                soldier=soldier,
                name=activity_name,
                start_date=day,
                end_date=day,
                subdivision=request.user.subdivision
            )

        if new_activity:
            left_activity = None
            right_activity = None
            try:
                left_activity = Activity.objects.get(end_date=day + datetime.timedelta(days=-1),
                                                     soldier=new_activity.soldier,
                                                     name=new_activity.name)
            except Activity.DoesNotExist:
                print('No "left" activity for the same soldier and same activity name.')

            try:
                right_activity = Activity.objects.get(start_date=day + datetime.timedelta(days=1),
                                                      soldier=new_activity.soldier,
                                                      name=new_activity.name)
            except Activity.DoesNotExist:
                print('No "right" activity for the same soldier nad same activity name.')

            # MERGING THE SAME ACTIVITIES
            if left_activity and not right_activity:
                new_activity.delete()
                left_activity.end_date = day
                left_activity.save()
            elif right_activity and not left_activity:
                new_activity.delete()
                right_activity.start_date = day
                right_activity.save()
            elif left_activity and right_activity:
                left_activity.end_date = right_activity.end_date
                right_activity.delete()
                new_activity.delete()
                left_activity.save()

        return redirect('show-diagram')


class SoldierList(LoginRequiredMixin, generic.ListView):
    template_name = 'diagram/soldier_list.html'

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision).order_by('last_name')


class SoldierDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'diagram/soldier_detail.html'

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision)

    def get_context_data(self, **kwargs):
        context = super(SoldierDetail, self).get_context_data(**kwargs)
        context['activities'] = Activity.objects.filter(soldier=self.get_object(), end_date__gte=now()).order_by(
            'start_date')
        return context


class SoldierUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/soldier_update.html'
    form_class = SoldierForm

    def form_valid(self, form):
        soldier = form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Zmodyfikowano dane żołnierza.')
        return redirect('soldier-detail', pk=soldier.pk)

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision)


class SoldierCreate(LoginRequiredMixin, generic.CreateView):
    template_name = 'diagram/soldier_create.html'
    form_class = SoldierForm
    model = Soldier

    def form_valid(self, form):
        new_soldier = form.save(commit=False)
        new_soldier.subdivision = self.request.user.subdivision
        new_soldier.save()

        messages.add_message(self.request, messages.SUCCESS, 'Dodano żołnierza.')

        return redirect('soldier-detail', pk=new_soldier.pk)


class SoldierDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = 'diagram/soldier_delete.html'
    model = Soldier

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Usunięto żołnierza.')
        return reverse('soldier-list')


class ActivityUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/activity_update.html'
    form_class = ActivityForm

    def form_valid(self, form):
        activity = form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Zmodyfikowano aktywność.')
        return redirect('soldier-detail', pk=activity.soldier.pk)

    def get_queryset(self):
        return Activity.objects.filter(subdivision=self.request.user.subdivision)


class ActivityDelete(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk, subdivision=request.user.subdivision)
        except Activity.DoesNotExist:
            raise Http404()

        soldier_pk = activity.soldier.pk
        messages.add_message(request, messages.SUCCESS, 'Usunięto aktywność.')
        activity.delete()

        return redirect('soldier-detail', pk=soldier_pk)


class ActivityCreate(LoginRequiredMixin, generic.CreateView):
    model = Activity
    template_name = 'diagram/activity_create.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityCreate, self).get_context_data(**kwargs)
        soldier = get_object_or_404(Soldier, pk=self.kwargs['soldier_pk'])
        context['soldier_pk'] = soldier.pk
        return context

    def get_form(self, form_class=None):
        form = super(ActivityCreate, self).get_form(form_class=ActivityForm)
        soldier = get_object_or_404(Soldier, pk=self.kwargs['soldier_pk'])
        form.fields['soldier'].initial = soldier
        form.fields['start_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        soldier = get_object_or_404(Soldier, pk=self.kwargs['soldier_pk'])
        activity = form.save(commit=False)
        activity.soldier = soldier
        activity.subdivision = self.request.user.subdivision
        activity.save()

        return redirect('soldier-detail', pk=soldier.pk)
