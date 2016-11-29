from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.forms.extras.widgets import SelectDateWidget

from .models import *

import datetime


class ProfileCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birth_date = forms.DateField(required=True, widget=SelectDateWidget(years=range(datetime.date.today().year, 1900, -1)))
    first_name = forms.CharField(required=False, help_text="Optional")
    last_name = forms.CharField(required=False, help_text="Optional")

    class Meta:
        model = User
        fields = ("username", "email", "birth_date", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile = Profile(user=user, birth_date=self.cleaned_data["birth_date"])
            profile.save()
        return user

class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email Or Username"), max_length=254)
    
class ActivityForm(forms.ModelForm):
    title = forms.CharField(required=True, max_length=200)
    description = forms.CharField(required=True, max_length=5000, widget=forms.Textarea)
    auto_register = forms.BooleanField(required=False, help_text="Selected: Users join automatically. Not selected: Author decides to accept or reject joining requests.")
    confirmation_period = forms.IntegerField(required=True, validators=[MinValueValidator(3)], initial=3, help_text="How many days before a session starts the assistance confirmation period?")
    age_minimum = forms.IntegerField(required=True, initial=18, help_text="Minimum age to attend this activity.")
    
    class Meta:
        model = Activity
        fields = ("title", "description", "auto_register", "confirmation_period", "age_minimum")


class SessionForm(forms.ModelForm):
    description = forms.CharField(required=True, max_length=500, widget=forms.Textarea)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    location = forms.CharField(required=True, max_length=100)
    
    class Meta:
        model = Session
        fields = ("description", "start_date", "end_date", "location")
