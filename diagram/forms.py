from django.forms import ModelForm

from diagram.models import Soldier


class SoldierForm(ModelForm):
    class Meta:
        model = Soldier
        exclude = ['subdivision']