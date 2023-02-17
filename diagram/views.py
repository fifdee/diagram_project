import time

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.timezone import now
from django.views import generic
import datetime
import holidays
from guest_user.mixins import AllowGuestUserMixin
from uuid import uuid4

from activity_colors.models import ActivityColor
from diagram.demo_account import create_demo_data, delete_demo_data_for_expired_guests
from diagram.forms import SoldierForm, ActivityFormSoldierDisabled, SoldierInfoUpdateForm, SoldierInfoNamesUpdateForm, \
    SoldierInfoAddForm, ActivityForm, EverydayActivityForm
from diagram.models import Soldier, Activity, SoldierInfo, EverydayActivity, Subdivision
from diagram.text_choices import ACTIVITY_NAMES, SOLDIER_INFO_NAME_CHANGE_PREFIX
from diagram.functions import activity_conflicts, get_soldier_activities, get_url_params, merge_neighbour_activities, \
    update_soldier_info_names, unassigned_activities_as_string, everyday_activity_conflicts, \
    everyday_activities_as_string, get_activities_count_for_day, reordered_activities_count


class DemoAccountCreate(AllowGuestUserMixin, generic.View):
    def get(self, request):
        user = request.user
        uid = str(uuid4())
        new_subdivision = Subdivision.objects.create(name='Przykładowy pododdział ' + uid, demo=True)
        user.subdivision = new_subdivision
        user.save()

        create_demo_data(new_subdivision)

        return redirect('show-diagram')


class DeleteDemoDataForExpiredGuests(generic.View):
    def get(self, request):
        if request.user.is_superuser:
            delete_demo_data_for_expired_guests()
        return redirect('show-diagram')

class ShowDiagram(generic.View):
    def get(self, request):
        if request.user.is_authenticated:
            t_1 = time.time()

            today = now().date()
            these_holidays = holidays.Poland(years=[today.year - 1, today.year, today.year + 1])

            soldiers = list(Soldier.objects.filter(subdivision=request.user.subdivision).order_by('last_name'))
            this_subdiv_act = list(Activity.objects.filter(subdivision=request.user.subdivision))
            this_subdiv_act_colors = list(ActivityColor.objects.filter(subdivision=request.user.subdivision))
            unassigned_activities = list(Activity.objects.filter(subdivision=request.user.subdivision, soldier=None))
            everyday_activities = list(EverydayActivity.objects.filter(subdivision=request.user.subdivision))

            activities = {}
            dates = []

            default_start_day = -1  # yesterday
            start_day = default_start_day

            try:
                start_day = int(self.request.GET['start_day'])
            except MultiValueDictKeyError:
                ...
            except ValueError:
                print('invalid value for start_day parameter')

            days_count_param = request.GET.get('days_count', None)
            try:
                if days_count_param and int(days_count_param) in range(4, 21):
                    request.session['days_count'] = int(days_count_param)
            except ValueError:
                ...
            days_count = request.session.get('days_count', 12)
            request.session['days_count'] = days_count

            for soldier in soldiers:
                activities[soldier] = {}
                for j in range(start_day, days_count + start_day):
                    this_date = today + datetime.timedelta(days=j)

                    this_day_activities = [act for act in this_subdiv_act if
                                           act.start_date <= this_date <= act.end_date]

                    this_date_with_info = (this_date, these_holidays.get(this_date),
                                               unassigned_activities_as_string([act for act in unassigned_activities if act.start_date <= this_date <= act.end_date])
                                           + everyday_activities_as_string(everyday_activities, this_day_activities)
                                           )
                    if this_date not in [x[0] for x in dates]:
                        dates.append(this_date_with_info)

                    activities[soldier][j] = {}
                    activities[soldier][j]['name'] = ''
                    activities[soldier][j]['date'] = this_date.strftime('%d.%m.%Y')
                    activities[soldier][j]['soldier_pk'] = soldier.pk

                    try:
                        activity = [act for act in this_subdiv_act if act.soldier == soldier and act.start_date <= this_date <= act.end_date][0]
                        activities[soldier][j]['name'] = activity
                        activities[soldier][j]['pk'] = activity.pk
                        activities[soldier][j]['description'] = activity.description

                        try:
                            activities[soldier][j]['color'] = [act_col for act_col in this_subdiv_act_colors
                                                               if act_col.subdivision == request.user.subdivision and
                                                               act_col.activity_name == activity.get_name_display()][0].color_hex

                        except ActivityColor.DoesNotExist:
                            messages.add_message(self.request, messages.WARNING,
                                                 f'Nie udało się pobrać danych koloru dla aktywności:'
                                                 f' {activity.get_name_display()}')

                    except Activity.DoesNotExist:
                        pass
                    except IndexError:
                        pass
                    except Activity.MultipleObjectsReturned:
                        messages.add_message(self.request, messages.WARNING,
                                             f'Konflikt aktywności dla żołnierza: {soldier}')

            activities_count = get_activities_count_for_day(subdivision=request.user.subdivision, day=today)
            activities_count['Do zajęć'] = len(soldiers) - sum(activities_count.values())
            activities_count['Ewidencyjnie'] = len(soldiers)
            activities_count['Obecni'] = activities_count['Do zajęć'] + activities_count['Służby'] + activities_count['Po służbie']
            activities_count = reordered_activities_count(activities_count)

            context = {
                'activities': activities,
                'activities_count': activities_count,
                'today': today,
                'range': range(4, 21),
                'default_start_day': default_start_day,
                'dates': sorted(dates, key=lambda x: x[0]),
                'holidays': these_holidays,
                'choices': sorted([a[0] for a in ACTIVITY_NAMES]),
            }

            print(f'time to compute diagram view: {time.time() - t_1} sec.')
            return render(request, template_name='diagram/show_diagram.html', context=context)
        else:
            return render(request, template_name='diagram/homepage.html')

    def post(self, request):
        if request.user.is_authenticated:
            soldier = Soldier.objects.get(pk=request.POST['soldier_pk'])
            activity_name = request.POST['activity_new']
            day = datetime.datetime.strptime(request.POST['date'], '%d.%m.%Y').date()

            activity_previous_pk = request.POST['activity_previous_pk']
            if activity_previous_pk != '':
                # MODIFYING OR SPLITTING PREVIOUS ACTIVITY
                previous_activity = Activity.objects.get(pk=activity_previous_pk)

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
                        subdivision=request.user.subdivision,
                        demo=request.user.subdivision.demo
                    )

            if activity_name != '':
                Activity.objects.create(
                    soldier=soldier,
                    name=activity_name,
                    start_date=day,
                    end_date=day,
                    subdivision=request.user.subdivision,
                    demo=request.user.subdivision.demo
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
            ...

        context = super(SoldierDetail, self).get_context_data(**kwargs)

        context['activities'] = get_soldier_activities(activity_age, soldier=self.get_object())

        soldier_fields = SoldierInfo.objects.filter(soldier=self.get_object())
        context['soldier_fields'] = []
        for soldier_field in soldier_fields:
            context['soldier_fields'].append(
                {'name': soldier_field.name, 'value': soldier_field.value, 'pk': soldier_field.pk})
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
        new_soldier.demo = self.request.user.subdivision.demo
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


class ActivityCreateSoldierBound(LoginRequiredMixin, generic.CreateView):
    model = Activity
    template_name = 'diagram/activity_create.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityCreateSoldierBound, self).get_context_data(**kwargs)
        soldier = get_object_or_404(Soldier, pk=self.kwargs['soldier_pk'])
        context['soldier_pk'] = soldier.pk
        return context

    def get_form(self, form_class=None):
        form = super(ActivityCreateSoldierBound, self).get_form(form_class=ActivityFormSoldierDisabled)
        soldier = get_object_or_404(Soldier, pk=self.kwargs['soldier_pk'])
        form.fields['soldier'].initial = soldier
        form.fields['start_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        activity = form.save(commit=False)
        activity.subdivision = self.request.user.subdivision
        activity.demo = self.request.user.subdivision.demo
        activity.save()
        messages.add_message(self.request, messages.SUCCESS, f'Dodano aktywność: {activity}')

        return redirect('soldier-detail', pk=self.kwargs['soldier_pk'])


class ActivityCreate(LoginRequiredMixin, generic.CreateView):
    model = Activity
    template_name = 'diagram/activity_create.html'

    def get_form(self, form_class=None):
        form = super(ActivityCreate, self).get_form(form_class=ActivityForm)
        form.fields['soldier'].queryset = Soldier.objects.filter(subdivision=self.request.user.subdivision)
        form.fields['start_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.widgets.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        activity = form.save(commit=False)
        activity.subdivision = self.request.user.subdivision
        activity.demo = self.request.user.subdivision.demo
        activity.save()
        messages.add_message(self.request, messages.SUCCESS, f'Dodano aktywność: {activity}')

        return redirect('activity-unassigned-and-everyday-list')


class EverydayActivityCreate(LoginRequiredMixin, generic.CreateView):
    model = EverydayActivity
    template_name = 'diagram/activity_create.html'
    fields = ['name', 'how_many']

    def form_valid(self, form):
        everyday_activity = form.save(commit=False)
        everyday_activity.subdivision = self.request.user.subdivision
        everyday_activity.demo = self.request.user.subdivision.demo
        conflicts = everyday_activity_conflicts(everyday_activity, EverydayActivity)
        if conflicts:
            form.add_error('name', 'Już istnieje codzienna aktywność tego typu.')
            return super().form_invalid(form)
        everyday_activity.save()
        messages.add_message(self.request, messages.SUCCESS, f'Dodano codzienną aktywność: {everyday_activity}')

        return redirect('activity-unassigned-and-everyday-list')


class ActivityUpdateSoldierBound(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/activity_update.html'
    form_class = ActivityFormSoldierDisabled

    def get_context_data(self, **kwargs):
        context = super(ActivityUpdateSoldierBound, self).get_context_data(**kwargs)
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


class ActivityUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/activity_update.html'
    form_class = ActivityForm

    def get_form(self, form_class=None):
        form = super(ActivityUpdate, self).get_form(form_class=ActivityForm)
        form.fields['soldier'].queryset = Soldier.objects.filter(subdivision=self.request.user.subdivision)
        return form

    def form_valid(self, form):
        activity = form.save()
        messages.add_message(self.request, messages.SUCCESS, f'Zmodyfikowano aktywność: {activity}')

        return redirect('activity-unassigned-and-everyday-list')

    def get_queryset(self):
        return Activity.objects.filter(subdivision=self.request.user.subdivision)


class EverydayActivityUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'diagram/activity_update.html'
    form_class = EverydayActivityForm

    def form_valid(self, form):
        everyday_activity = form.save(commit=False)
        conflicts = everyday_activity_conflicts(everyday_activity, EverydayActivity)
        if conflicts:
            form.add_error('name', 'Już istnieje codzienna aktywność tego typu.')
            return super().form_invalid(form)
        everyday_activity.save()
        messages.add_message(self.request, messages.SUCCESS, f'Zmodyfikowano codzienną aktywność: {everyday_activity}')

        return redirect('activity-unassigned-and-everyday-list')

    def get_queryset(self):
        return EverydayActivity.objects.filter(subdivision=self.request.user.subdivision)


class ActivityDelete(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk, subdivision=request.user.subdivision)
        except Activity.DoesNotExist:
            raise Http404()

        activity.delete()
        messages.add_message(request, messages.SUCCESS, f'Usunięto aktywność {activity}')

        if activity.soldier:
            soldier_pk = activity.soldier.pk
            return redirect('soldier-detail', pk=soldier_pk)
        else:
            return redirect('activity-unassigned-and-everyday-list')


class EverydayActivityDelete(LoginRequiredMixin, generic.View):
    def get(self, request, pk):
        try:
            everyday_activity = EverydayActivity.objects.get(pk=pk, subdivision=request.user.subdivision)
        except Activity.DoesNotExist:
            raise Http404()

        everyday_activity.delete()
        messages.add_message(request, messages.SUCCESS, f'Usunięto codzienną aktywność {everyday_activity}')

        return redirect('activity-unassigned-and-everyday-list')


class SoldierInfoUpdate(LoginRequiredMixin, generic.View):
    def get(self, request, soldier_pk):
        try:
            soldier = Soldier.objects.get(pk=soldier_pk, subdivision=request.user.subdivision)
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

        try:
            subdivision = Soldier.objects.get(pk=soldier_pk, subdivision=request.user.subdivision).subdivision
        except Soldier.DoesNotExist:
            raise Http404()

        update_soldier_info_names(subdivision, soldier_info_fields_names)
        messages.add_message(self.request, messages.SUCCESS,
                             'Zapisano nazwy danych wszystkich żołnierzy w pododdziale')

        return redirect('soldier-detail', pk=soldier_pk)


class SoldierInfoAdd(LoginRequiredMixin, generic.CreateView):
    template_name = 'diagram/soldier_info_add.html'
    form_class = SoldierInfoAddForm

    def get_context_data(self, **kwargs):
        context = super(SoldierInfoAdd, self).get_context_data(**kwargs)
        context['soldier_pk'] = self.kwargs['soldier_pk']
        return context

    def form_valid(self, form):
        soldier_info = form.save(commit=False)
        try:
            soldier_info.soldier = Soldier.objects.get(pk=self.kwargs['soldier_pk'],
                                                       subdivision=self.request.user.subdivision)
        except Soldier.DoesNotExist:
            raise Http404()

        soldier_info.save()

        # create same data field for other soldiers in the same division
        same_subdivision_soldiers = Soldier.objects.filter(subdivision=soldier_info.soldier.subdivision).exclude(
            pk=self.kwargs['soldier_pk'])
        for soldier in same_subdivision_soldiers:
            SoldierInfo.objects.create(
                soldier=soldier,
                name=soldier_info.name,
            )
        messages.add_message(self.request, messages.SUCCESS,
                             'Dodano nowe pole danych dla wszystkich żołnierzy w pododdziale')

        return redirect('soldier-detail', pk=self.kwargs['soldier_pk'])


class SoldierInfoDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = 'diagram/soldier_info_delete.html'
    model = SoldierInfo

    def get_queryset(self):
        return SoldierInfo.objects.filter(soldier__subdivision=self.request.user.subdivision)

    def form_valid(self, form):
        this_soldier_info = self.get_object()
        soldier_pk = this_soldier_info.soldier.pk

        # deleting soldier info fields with this soldier info name for other soldiers in the same subdivision
        same_subdivision_soldiers = Soldier.objects.filter(subdivision=this_soldier_info.soldier.subdivision).exclude(
            pk=this_soldier_info.soldier.pk)
        for soldier in same_subdivision_soldiers:
            try:
                SoldierInfo.objects.get(soldier=soldier, name=this_soldier_info.name).delete()
            except SoldierInfo.DoesNotExist:
                print(f"{soldier} doesn't have {this_soldier_info.name} field")

        this_soldier_info.delete()

        messages.add_message(self.request, messages.SUCCESS, 'Usunięto pole danych.')

        return redirect('soldier-detail', pk=soldier_pk)


class ActivityUnassignedAndEverydayList(LoginRequiredMixin, generic.View):
    def get(self, request):
        context = {
            'unassigned_activities': Activity.objects.filter(subdivision=self.request.user.subdivision, soldier=None),
            'everyday_activities': EverydayActivity.objects.filter(subdivision=self.request.user.subdivision)
        }
        return render(request, 'diagram/activity_unassigned_and_everyday_list.html', context)
