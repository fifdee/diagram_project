from django import forms
from django.forms import ModelForm

from diagram.models import Soldier, Activity


class SoldierForm(ModelForm):
    class Meta:
        model = Soldier
        exclude = ['subdivision']


class SoldierDetailForm(ModelForm):
    class Meta:
        model = Soldier
        exclude = ['subdivision', 'rank', 'first_name', 'last_name']


class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        exclude = ['subdivision']

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['soldier'].disabled = True
