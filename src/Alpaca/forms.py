from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts import get_object_or_404 

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from .models import *

import hashlib
import datetime


class ProfileCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('E-mail'))
    birth_date = forms.DateField(required=True, label=_('Birth date'), widget=SelectDateWidget(years=range(datetime.date.today().year, 1900, -1)))
    first_name = forms.CharField(required=False, label=_('First Name'), help_text=_("Optional"))
    last_name = forms.CharField(required=False, label=_('Last Name'), help_text=_("Optional"))

    language_options = ( ("en", _("English")),
                         ("es", _("Spanish")),
                         ("eus", _("Euskera")) )
    language_preference = forms.ChoiceField(label=_('Language'), required=True, choices=language_options, help_text=_('In which language would you prefer to use Alpaca?'))

    class Meta:
        model = User
        fields = ("username", "email", "birth_date", "password1", "password2", "first_name", "last_name", "language_preference")

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.is_active = False
            user.save()
            profile = Profile(user=user, birth_date=self.cleaned_data["birth_date"], language_preference=self.cleaned_data["language_preference"])
            profile.save()
        
        return user



class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    first_name = forms.CharField(label=_('First Name'), required=False, help_text=_("Optional"))
    last_name = forms.CharField(label=_('Last Name'), required=False, help_text=_("Optional"))
    birth_date = forms.DateField(label=_('Birth date'), widget=SelectDateWidget(years=range(datetime.date.today().year, 1900, -1)))

    show_birthday = forms.BooleanField(label=_('Show your birthday?'), required=False)
    show_email = forms.BooleanField(label=_('Show your e-mail?'), required=False)
    show_real_name = forms.BooleanField(label=_('Show your real name?'), required=False)  
    
    format_options = ( ("nick (full_name)", _("Username (Full Name)")),
                       ("full_name (nick)", _("Full Name (Username)")),
                       ("nick (first_name)", _("Username (First Name)")),
                       ("nick (last_name)", _("Username (Last Name)")),
                       ("first_name (nick)", _("First Name (Username)")),
                       ("last_name (nick)", _("Last Name (Username)")),
                    )
    display_name_format = forms.ChoiceField(label=_('How should your name be displayed?'), required=True, choices=format_options, help_text=_('You can ignore this if you chose not to show your name.'))

    language_options = ( ("en", _("English")),
                         ("es", _("Spanish")),
                         ("eus", _("Euskera")) )
    language_preference = forms.ChoiceField(label=_('Language'), required=True, choices=language_options, help_text=_('In which language would you prefer to use Alpaca?'))

    class Meta:
        model = Profile
        fields = ("avatar", "first_name", "last_name", "birth_date", "show_birthday", "show_email", "show_real_name", "display_name_format", "language_preference")
   





class ActivityForm(forms.ModelForm):
    title = forms.CharField(required=True, label=_('Title'), max_length=200)
    description = forms.CharField(required=True, label=_('Description'), max_length=5000, widget=forms.Textarea)
    cover = forms.ImageField(required=False, help_text=_("Covers are optional. You may change it at any time."))
    
    city = forms.CharField(required=True, label=_('City'), max_length=100, help_text=_("In which city will this activity take place?"))

    auto_register = forms.BooleanField(required=False, label=_('Allow auto-registration?'), help_text=_("Selected: Users join automatically. Not selected: Author decides to accept or reject joining requests."))
    confirmation_period = forms.IntegerField(required=True, label=_('Confirmation period'), validators=[MinValueValidator(3)], initial=3, help_text=_("How many days before a session starts the assistance confirmation period?"))
    age_minimum = forms.IntegerField(required=True, label=_('Age minimum'), initial=18, help_text=_("Minimum age to attend this activity."))
    
    class Meta:
        model = Activity
        fields = ("title", "description", "cover", "city", "auto_register", "confirmation_period", "age_minimum")


class SessionForm(forms.ModelForm):
    description = forms.CharField(required=True, label=_('Description'), max_length=500, widget=forms.Textarea)
    start_date = forms.DateTimeField(required=True, label=_('Start date and time'), help_text=_("Example: 1984-11-15 19:25:36"))
    end_date = forms.DateTimeField(required=True, label=_('End date and time'), help_text=_("Example: 1984-11-15 19:25:36"))
    location = forms.CharField(required=True, label=_('Location'), max_length=100, help_text=_("Where (place, address) will this session take place?"))
    
    class Meta:
        model = Session
        fields = ("description", "start_date", "end_date", "location")

    def clean(self):
        super(SessionForm, self).clean()
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if start_date <= timezone.now():
            msg = _("The start date and time must be greater than today's date.")
            self._errors["start_date"] = self.error_class([msg])

        if end_date < start_date:
            msg = _("The end date and time must be greater than the start date.")
            self._errors["end_date"] = self.error_class([msg])

## MINOR FORMS ##
class ForgotPasswordForm(forms.Form):
    email_or_username = forms.CharField(label=_("E-mail Or Username"), max_length=254)


class NewPasswordForm(forms.Form):
    new_password = forms.CharField(required=True, label=_("New password:"), widget=forms.PasswordInput())
    repeat_password = forms.CharField(required=True, label=_("Repeat new password:"), widget=forms.PasswordInput())
 
    class Meta:
        fields = ("new_password", "repeat_password")

    def is_valid(self, user):
        return self.data['new_password'] == self.data['repeat_password']
        
    def save(self, user, commit=True):    
        user.set_password(self.data['new_password'])
        if commit:
            user.save()
        return user


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, label=_("Old password:"), widget=forms.PasswordInput())
    new_password = forms.CharField(required=True, label=_("New password:"), widget=forms.PasswordInput())
    repeat_password = forms.CharField(required=True, label=_("Repeat new password:"), widget=forms.PasswordInput())
 
    class Meta:
        fields = ("old_password", "new_password", "repeat_password")

    def is_valid(self, user):
        return user.check_password(self.data['old_password']) and self.data['new_password'] == self.data['repeat_password']
        
    def save(self, user, commit=True):    
        user.set_password(self.data['new_password'])
        if commit:
            user.save()
        return user

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(required=True, label=_("From:"), initial=datetime.datetime.now(), widget=SelectDateWidget(years=range(datetime.date.today().year, 1900, -1)))
    end_date = forms.DateField(required=True, label=_("To:"), initial=datetime.datetime.now(), widget=SelectDateWidget(years=range(datetime.date.today().year, 1900, -1)))
 
    class Meta:
        fields = ("start_date", "end_date")

    def is_valid(self):
        super(DateRangeFilterForm, self).is_valid()
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if end_date < start_date:
           msg = _("The end date must be greater than the start date.")
           self._errors["end_date"] = self.error_class([msg])
           return False
        return True
        
    def get_activities(self, activity_list):    
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        
        activity_list = filter(lambda a: a.get_next_session() != None, activity_list)
        activity_list = sorted(activity_list, 
                              key = lambda a: (a.get_next_session().start_date.date() >= start_date 
                                               and a.get_next_session().start_date.date() <= end_date), 
                              reverse=True)
        return activity_list