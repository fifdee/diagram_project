
from allauth.account.forms import SignupForm
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from diagram.models import Subdivision

class SimpleSignupForm(SignupForm):
    subdivision = forms.CharField(max_length=30, label='Pododdział', widget=forms.TextInput(
            attrs={"placeholder": "Nazwa pododdziału"}
        ),)

    def clean(self):
        super(SimpleSignupForm, self).clean()

        subdivision = self.cleaned_data.get("subdivision")
        if Subdivision.objects.filter(name=subdivision).count() > 0:
            self.add_error("subdivision", "Pododdział o takiej nazwie już istnieje, wybierz inną nazwę.")

        return self.cleaned_data


    def save(self, request):
        user = super(SimpleSignupForm, self).save(request)

        subdivision = Subdivision.objects.create(name=self.cleaned_data['subdivision'])

        user.subdivision = subdivision
        user.save()
        return user
