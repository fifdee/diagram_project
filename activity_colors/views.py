from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from activity_colors.forms import ActivityColorModelForm
from activity_colors.models import ActivityColor


# Create your views here.
class ActivityColorsUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        colors = ActivityColor.objects.filter(subdivision=request.user.subdivision)
        forms = [{'instance': ActivityColorModelForm(instance=x), 'name': x.activity_name} for x in colors]

        context = {
            'forms': sorted(forms, key=lambda x: x['name'])
        }
        return render(request, template_name='diagram/activity_color_update.html', context=context)

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(ActivityColor, activity_name=request.POST['activity_name'],
                                     subdivision=request.user.subdivision)
        print(request.POST)
        instance.color_hex = request.POST['color_hex']
        instance.save()

        messages.add_message(self.request, messages.SUCCESS,
                             f'Zapisano dane koloru aktywności {request.POST["activity_name"]}.')
        return redirect(reverse('activity-colors-update') + f'#{request.POST["activity_name"]}')
