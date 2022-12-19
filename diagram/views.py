from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.timezone import now
from django.views import generic
import datetime

from diagram.forms import SoldierForm, ActivityForm, SoldierInfoUpdateForm, SoldierInfoNamesUpdateForm
from diagram.models import Soldier, Activity, SoldierInfo
from diagram.text_choices import ACTIVITY_NAMES, SOLDIER_INFO_NAME_CHANGE_PREFIX
from diagram.functions import activity_conflicts, get_soldier_activities, get_url_params, merge_neighbour_activities, \
    update_soldier_info_names


class ShowDiagram(LoginRequiredMixin, generic.View):
    def get(self, request):
        today = now().date()
        soldiers = Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name')
        activities = {}
        dates = set()

        default_start_day = -1  # yesterday
        start_day = default_start_day
        default_days_count = 12  # TODO load saved setting from settings model
        days_count = default_days_count
        try:
            days_count = int(self.request.GET['days_count'])
            start_day = int(self.request.GET['start_day'])
        except MultiValueDictKeyError:
            print('using default days_count and/or start_day value')
        except ValueError:
            print('invalid value for days_count and/or start_day parameter')

        if days_count > 20:
            days_count = 20

        for soldier in soldiers:
            activities[soldier] = {}
            for j in range(start_day, days_count + start_day):
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
                except Activity.MultipleObjectsReturned:
                    messages.add_message(self.request, messages.WARNING,
                                         f'Konflikt aktywności dla żołnierza: {soldier}')

        context = {
            'activities': activities,
            'today': today,
            'range': range(4, 21),
            'default_days_count': default_days_count,
            'default_start_day': default_start_day,
            'dates': sorted(dates),
            'choices': sorted([a[0] for a in ACTIVITY_NAMES]),
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

        if activity_name != '':
            Activity.objects.create(
                soldier=soldier,
                name=activity_name,
                start_date=day,
                end_date=day,
                subdivision=request.user.subdivision
            )

        url_params = get_url_params(request.POST['days_count'], request.POST['start_day'])
        return redirect(f"{reverse_lazy('show-diagram')}{url_params}")


class SoldierList(LoginRequiredMixin, generic.ListView):
    template_name = 'diagram/soldier_list.html'

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision).order_by('last_name')


class SoldierDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'diagram/soldier_detail.html'

    def get_queryset(self):
        return Soldier.objects.filter(subdivision=self.request.user.subdivision)

    def get_context_data(self, **kwargs):
        activity_age = 'current'
        try:
            activity_age = self.request.GET['activity_age']
        except MultiValueDictKeyError:
            print('"start" parameter in URL not found - using "current" as default')

        print(activity_age)
        context = super(SoldierDetail, self).get_context_data(**kwargs)

        context['activities'] = get_soldier_activities(activity_age, soldier=self.get_object())

        soldier_fields = SoldierInfo.objects.filter(soldier=self.get_object())
        context['soldier_fields'] = []
        for soldier_field in soldier_fields:
            context['soldier_fields'].append({'name': soldier_field.name, 'value': soldier_field.value})
        return context


class SoldierUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/soldier_update.html'
    form_class = SoldierForm

    def get_context_data(self, **kwargs):
        context = super(SoldierUpdate, self).get_context_data(**kwargs)
        soldier = get_object_or_404(Soldier, pk=self.get_object().pk)
        context['soldier_pk'] = soldier.pk
        return context

    def form_valid(self, form):
        soldier = form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Zapisano stopień, imię i nazwisko żołnierza.')
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
        activity = form.save(commit=False)
        activity.subdivision = self.request.user.subdivision
        activity.save()
        messages.add_message(self.request, messages.SUCCESS, f'Dodano aktywność: {activity}')

        return redirect('soldier-detail', pk=self.kwargs['soldier_pk'])


class ActivityUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/activity_update.html'
    form_class = ActivityForm

    def get_context_data(self, **kwargs):
        context = super(ActivityUpdate, self).get_context_data(**kwargs)
        soldier = get_object_or_404(Soldier, pk=self.get_object().soldier.pk)
        context['soldier_pk'] = soldier.pk
        return context

    def form_valid(self, form):
        activity = form.save()
        soldier = activity.soldier
        messages.add_message(self.request, messages.SUCCESS, f'Zmodyfikowano aktywność: {activity}')

        return redirect('soldier-detail', pk=soldier.pk)

    def get_queryset(self):
        return Activity.objects.filter(subdivision=self.request.user.subdivision)


class ActivityDelete(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk, subdivision=request.user.subdivision)
        except Activity.DoesNotExist:
            raise Http404()

        soldier_pk = activity.soldier.pk
        messages.add_message(request, messages.SUCCESS, f'Usunięto aktywność {activity}')
        activity.delete()

        return redirect('soldier-detail', pk=soldier_pk)


class SoldierInfoUpdate(LoginRequiredMixin, generic.View):
    def get(self, request, soldier_pk):
        try:
            soldier = Soldier.objects.get(pk=soldier_pk)
        except Soldier.DoesNotExist:
            messages.add_message(request, messages.WARNING, f'Nie znaleziono żołnierza o ID = {soldier_pk}')
            return redirect('soldier-list')

        context = {
            'message': soldier,
            'soldier_pk': soldier_pk,
            'form': SoldierInfoUpdateForm(soldier_pk=soldier_pk)
        }
        return render(request, template_name='diagram/soldier_info_update.html', context=context)

    def post(self, request, soldier_pk):
        soldier_info = SoldierInfo.objects.filter(soldier_id=soldier_pk)
        for specific_info in soldier_info:
            specific_info.value = request.POST[specific_info.name]
            specific_info.save()

        messages.add_message(self.request, messages.SUCCESS, 'Zapisano dane żołnierza.')
        return redirect('soldier-detail', pk=soldier_pk)


class SoldierInfoNamesUpdate(LoginRequiredMixin, generic.View):
    def get(self, request, soldier_pk):
        context = {'message': 'Zmodyfikuj nazwy danych wszystkich żołnierzy w pododdziale.',
                   'soldier_pk': soldier_pk,
                   'form': SoldierInfoNamesUpdateForm(soldier_pk=soldier_pk)}
        return render(request, template_name='diagram/soldier_info_update.html', context=context)

    def post(self, request, soldier_pk):
        soldier_info_fields_names = []
        for prev_name, new_name in request.POST.items():
            if SOLDIER_INFO_NAME_CHANGE_PREFIX in prev_name:
                soldier_info_fields_names.append((prev_name.replace(SOLDIER_INFO_NAME_CHANGE_PREFIX, ''), new_name))

        subdivision = Soldier.objects.get(pk=soldier_pk).subdivision
        update_soldier_info_names(subdivision, soldier_info_fields_names)
        messages.add_message(self.request, messages.SUCCESS,
                             'Zapisano nazwy danych wszystkich żołnierzy w pododdziale.')

        return redirect('soldier-detail', pk=soldier_pk)
