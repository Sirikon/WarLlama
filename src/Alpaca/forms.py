from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts import get_object_or_404 

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

class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(disabled=True)
    show_birthday = forms.BooleanField(required=False)
    show_email = forms.BooleanField(required=False)
    show_real_name = forms.BooleanField(required=False)  
    
    format_options = ( ("nick (full_name)", "Username (Full Name)"),
                       ("full_name (nick)", "Full Name (Username)"),
                       ("nick (first_name)", "Username (First Name)"),
                       ("nick (last_name)", "Username (Last Name)"),
                       ("first_name (nick)", "First Name (Username)"),
                       ("last_name (nick)", "Last Name (Username)"),
                )
    display_name_format = forms.ChoiceField(required=True, choices=format_options)

    class Meta:
        model = Profile
        fields = ("birth_date", "show_birthday", "show_email", "show_real_name", "display_name_format")

class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Email Or Username"), max_length=254)

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, label="Old password:", widget=forms.PasswordInput())
    new_password = forms.CharField(required=True, label="New password:", widget=forms.PasswordInput())
    repeat_password = forms.CharField(required=True, label="Repeat new password:", widget=forms.PasswordInput())
 
    class Meta:
        fields = ("old_password", "new_password", "repeat_password")

    def is_valid(self, user):
        return user.check_password(self.data['old_password']) and self.data['new_password'] == self.data['repeat_password']
        
    def save(self, user, commit=True):    
        user.set_password(self.data['new_password'])
        if commit:
            user.save()
        return user


class ActivityForm(forms.ModelForm):
    title = forms.CharField(required=True, max_length=200)
    description = forms.CharField(required=True, max_length=5000, widget=forms.Textarea)
    city = forms.CharField(required=True, max_length=100, help_text="In which city will this activity take place?")
    auto_register = forms.BooleanField(required=False, help_text="Selected: Users join automatically. Not selected: Author decides to accept or reject joining requests.")
    confirmation_period = forms.IntegerField(required=True, validators=[MinValueValidator(3)], initial=3, help_text="How many days before a session starts the assistance confirmation period?")
    age_minimum = forms.IntegerField(required=True, initial=18, help_text="Minimum age to attend this activity.")
    
    class Meta:
        model = Activity
        fields = ("title", "description", "city", "auto_register", "confirmation_period", "age_minimum")

class SessionForm(forms.ModelForm):
    description = forms.CharField(required=True, max_length=500, widget=forms.Textarea)
    start_date = forms.DateTimeField(required=True, help_text="Example: 1984-11-15 19:25:36")
    end_date = forms.DateTimeField(required=True, help_text="Example: 1984-11-15 19:25:36")
    location = forms.CharField(required=True, max_length=100, help_text="Where (place, address) will this activity take place?")
    
    class Meta:
        model = Session
        fields = ("description", "start_date", "end_date", "location")
