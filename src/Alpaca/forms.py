from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator

from .models import *


class ProfileCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile = Profile(user=user)
            profile.save()
        return user

class ActivityForm(forms.ModelForm):
    title = forms.CharField(required=True, max_length=200)
    description = forms.CharField(required=True, max_length=500)
    auto_register = forms.BooleanField(required=False)
    confirmation_period = forms.IntegerField(required=True, validators=[MinValueValidator(3)])
    age_minimum = forms.IntegerField(required=True)
    
    class Meta:
        model = Activity
        fields = ("title", "description", "auto_register", "confirmation_period", "age_minimum")


class SessionForm(forms.ModelForm):
    description = forms.CharField(required=True, max_length=500)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    location = forms.CharField(required=True, max_length=100)
    
    class Meta:
        model = Session
        fields = ("description", "start_date", "end_date", "location")