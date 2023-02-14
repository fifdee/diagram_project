from crispy_forms.helper import FormHelper
from django import forms
from django.forms import ModelForm

from activity_colors.models import ActivityColor


class ActivityColorModelForm(ModelForm):
    class Meta:
        model = ActivityColor
        exclude = ['subdivision', 'activity_name', 'demo']

    def __init__(self, *args, **kwargs):
        super(ActivityColorModelForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False