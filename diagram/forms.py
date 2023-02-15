from django import forms
from django.forms import ModelForm

from diagram.models import Soldier, Activity, SoldierInfo, EverydayActivity
from diagram.text_choices import SOLDIER_INFO_NAME_CHANGE_PREFIX

class SoldierForm(ModelForm):
    class Meta:
        model = Soldier
        exclude = ['subdivision', 'demo']


class SoldierInfoUpdateForm(forms.Form):
    def __init__(self, **kwargs):
        super().__init__()
        fields = SoldierInfo.objects.filter(soldier_id=kwargs['soldier_pk'])

        for field in fields:
            self.fields[field.name] = forms.CharField(max_length=30, required=False, initial=field.value)


class SoldierInfoNamesUpdateForm(forms.Form):
    def __init__(self, **kwargs):
        super().__init__()
        fields = SoldierInfo.objects.filter(soldier_id=kwargs['soldier_pk'])

        for field in fields:
            self.fields[f'{SOLDIER_INFO_NAME_CHANGE_PREFIX}{field.name}'] = forms.CharField(max_length=30,
                                                                                            min_length=3,
                                                                                            required=True,
                                                                                            initial=field.name)


class SoldierInfoAddForm(forms.ModelForm):
    class Meta:
        model = SoldierInfo
        fields = ['name']


class ActivityFormSoldierDisabled(ModelForm):
    class Meta:
        model = Activity
        exclude = ['subdivision', 'demo']

    def __init__(self, *args, **kwargs):
        super(ActivityFormSoldierDisabled, self).__init__(*args, **kwargs)
        self.fields['soldier'].disabled = True


class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        exclude = ['subdivision', 'demo']


class EverydayActivityForm(ModelForm):
    class Meta:
        model = EverydayActivity
        exclude = ['subdivision', 'demo']
