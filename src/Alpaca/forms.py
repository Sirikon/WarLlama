from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts import get_object_or_404 

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _ ## For Multi-Language

from models import *

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
    
    terms_conditions = forms.BooleanField(
                        required=True, 
                        label= str(_('I accept the Terms and Conditions')), 
                    )
                    
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
        model = User
        fields = ("avatar", "first_name", "last_name", "birth_date", "show_birthday", "show_email", "show_real_name", "display_name_format", "language_preference")

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].initial = self.instance.profile.avatar
        self.fields['birth_date'].initial = self.instance.profile.birth_date
        self.fields['show_birthday'].initial = self.instance.profile.show_birthday
        self.fields['show_email'].initial = self.instance.profile.show_email
        self.fields['show_real_name'].initial = self.instance.profile.show_real_name
        self.fields['display_name_format'].initial = self.instance.profile.display_name_format
        self.fields['language_preference'].initial = self.instance.profile.language_preference

    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)

        if commit:
            user.save()
            user.profile.avatar = self.cleaned_data["avatar"]
            user.profile.birth_date = self.cleaned_data["birth_date"]
            user.profile.show_birthday = self.cleaned_data["show_birthday"]
            user.profile.show_email = self.cleaned_data["show_email"]
            user.profile.show_real_name = self.cleaned_data["show_real_name"]
            user.profile.display_name_format = self.cleaned_data["display_name_format"]
            user.profile.language_preference = self.cleaned_data["language_preference"]
            user.profile.save()
        
        return user
        
class GroupForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    name = forms.CharField(required=True, label=_('Group Name'))
    description = forms.CharField(required=True, label=_('Description'), max_length=5000, widget=forms.Textarea)
    email = forms.EmailField(required=True, label=_('E-mail'))

    show_email = forms.BooleanField(label=_("Show the group's e-mail?"), required=False)
    auto_register_users = forms.BooleanField(
                            required=False, 
                            label=_('Allow user auto-registration?'), 
                            help_text=_("Selected: Users join the group automatically. Not selected: Admins decide to accept or reject joining requests.")
                        )
    auto_register_activities = forms.BooleanField(
                            required=False,
                            label=_('Allow activity auto-registration?'),
                            help_text=_("Your group may have organize activities! Are members allowed to relate any of their activities to this group?")
                        )

    class Meta:
        model = Group
        fields = ("logo", "name", "description", "email", "show_email", "auto_register_users", "auto_register_activities")
   
    def save_new(self, user):
        group = super(GroupForm, self).save(commit=False)
        group.new(timezone.now(), user)
        group.logo = self.cleaned_data["logo"]
        group.save()        
        return group
       
    def save(self, commit=True):
        group = super(GroupForm, self).save(commit=False)
        if commit:
            group.logo = self.cleaned_data["logo"]
            group.save()        
        return group  


class ActivityForm(forms.ModelForm):
    title = forms.CharField(required=True, label=_('Title'), max_length=200)
    description = forms.CharField(required=True, label=_('Description'), max_length=5000, widget=forms.Textarea)
    cover = forms.ImageField(required=False, help_text=_("Covers are optional. You may change it at any time."))

    cover_disclaimer = forms.CharField( disabled=True, 
                                        widget=forms.Textarea(attrs={ 'rows': 3, 'cols': 10, 'style':'resize:none;'}), 
                                        label="", 
                                        initial=_("We would like to remind you that some images are copyrighted. We do not take responsibility for any copyright infrigements. The images will be deleted upon request of their rightful owner or their lawyers. Please, be aware of the rights you have over the image you want to upload before using it."))
    
    city = forms.CharField(required=True, label=_('City'), max_length=100, help_text=_("In which city will this activity take place?"))

    auto_register = forms.BooleanField(required=False, label=_('Allow auto-registration?'), help_text=_("Selected: Users join automatically. Not selected: Author decides to accept or reject joining requests."))
    confirmation_period = forms.IntegerField(required=True, label=_('Confirmation period'), validators=[MinValueValidator(3)], initial=3, help_text=_("How many days before a session starts the assistance confirmation period?"))
    age_minimum = forms.IntegerField(required=True, label=_('Age minimum'), initial=18, help_text=_("Minimum age to attend this activity."))
    
    ## ----------------------------------------
    def __init__(self, group_list, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)

        group_choices = Group.objects.filter(pk__in=group_list) #self.to_tuples(group_list)

        self.fields['group'] = forms.ModelChoiceField (
            label=_('Group'), 
            required=False, 
            queryset=group_choices,
            help_text=_('Is this activity related to any of your groups? Depending on the group, the activity may need to be accepted first.')
        )

    class Meta:
        model = Activity
        fields = ("title", "description", "cover", "cover_disclaimer", "group", "city", "auto_register", "confirmation_period", "age_minimum")

    def save_new(self, user):
        activity = super(ActivityForm, self).save(commit=False)
        activity.new(timezone.now(), user)  
        group = self.cleaned_data["group"]
        activity.set_group(group)
        activity.save()
        return activity

    def save(self, commit=True):
        activity = super(ActivityForm, self).save(commit=False)

        group = self.cleaned_data["group"]
        activity.set_group(group)

        if commit:
            activity.cover = self.cleaned_data["cover"]
            activity.save()        
        return activity


class ActivityForEventForm(forms.ModelForm):
    title = forms.CharField(required=True, label=_('Title'), max_length=200)
    description = forms.CharField(required=True, label=_('Description'), max_length=5000, widget=forms.Textarea)
    cover = forms.ImageField(required=False, help_text=_("Covers are optional. You may change it at any time."))
    cover_disclaimer = forms.CharField( disabled=True, 
                                        widget=forms.Textarea(attrs={ 'rows': 3, 'cols': 10, 'style':'resize:none;'}), 
                                        label="", 
                                        initial=_("We would like to remind you that some images are copyrighted. We do not take responsibility for any copyright infrigements. The images will be deleted upon request of their rightful owner or their lawyers. Please, be aware of the rights you have over the image you want to upload before using it."))
    
    auto_register = forms.BooleanField(required=False, label=_('Allow auto-registration?'), help_text=_("Selected: Users join automatically. Not selected: Author decides to accept or reject joining requests."))
    confirmation_period = forms.IntegerField(required=True, label=_('Confirmation period'), validators=[MinValueValidator(3)], initial=3, help_text=_("How many days before a session starts the assistance confirmation period?"))
    age_minimum = forms.IntegerField(required=True, label=_('Age minimum'), initial=18, help_text=_("Minimum age to attend this activity."))
    
    ## ----------------------------------------
    def __init__(self, group, event, *args, **kwargs):
        super(ActivityForEventForm, self).__init__(*args, **kwargs)

        self.fields['event_name'] = forms.CharField ( label=_('Event'), required=True, initial=event.title, disabled=True )
        self.fields['city']  = forms.CharField( label=_('City'), required=True, initial=event.city, disabled=True )

    class Meta:
        model = Activity
        fields = ("title", "description", "cover", "cover_disclaimer", "city", "auto_register", "confirmation_period", "age_minimum")
  
    def clean(self):
        super(ActivityForEventForm, self).clean()
        
        event = get_object_or_404(Event, title=self.cleaned_data["event_name"]) 
        age_minimum = self.cleaned_data.get("age_minimum")

        if age_minimum < event.age_minimum:
            msg = _("The event's minimum attendant age is {age}. You activity's minimum age must be greater or equal to the event's.").format(age = event.age_minimum)
            self._errors["age_minimum"] = self.error_class([msg])

    def save_new(self, user):
        activity = super(ActivityForEventForm, self).save(commit=False)
        activity.new(timezone.now(), user)  

        event = get_object_or_404(Event, title=self.cleaned_data["event_name"]) 
        activity.set_event(event)

        activity.save()
        return activity

    def save(self, commit=True):
        activity = super(ActivityForEventForm, self).save(commit=False)
        if commit:
            activity.cover = self.cleaned_data["cover"]
            activity.save()        
        return activity


class SessionForm(forms.ModelForm):
    description = forms.CharField(required=True, label=_('Description'), max_length=500, widget=forms.Textarea)
    start_date = forms.DateTimeField(required=True, label=_('Start date and time'), help_text=_("Example: 1984-11-15 19:25:36"))
    end_date = forms.DateTimeField(required=True, label=_('End date and time'), help_text=_("Example: 1984-11-15 19:25:36"))
    location = forms.CharField(required=True, label=_('Location'), max_length=100, help_text=_("Where (place, address) will this session take place?"))
    
    ## ----------------------------------------
    def __init__(self, activity, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

        self.activity = activity


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
            
        
        activity = self.activity
        if activity.event != None:
            event = activity.event

            if start_date < event.start_date or start_date > event.end_date:
                msg = _("The event start date is {start_date} and end date is {end_date}. Your session must start in between those dates.")
                msg = msg.format( start_date=event.start_date.date(), 
                                end_date=event.end_date.date() )
                self._errors["start_date"] = self.error_class([msg])

            if end_date > event.end_date:
                msg = _("The event start date is {start_date} and end date is {end_date}. Your session must end in between those dates.")
                msg = msg.format( start_date=event.start_date.date(), 
                                end_date=event.end_date.date() )
                self._errors["start_date"] = self.error_class([msg])


    def save_new(self, activity):
        session = super(SessionForm, self).save(commit=False)
        session.new(activity)  
        session.save()
        return session


class EventForm(forms.ModelForm):
    cover = forms.ImageField(required=False, help_text=_("This is the image that will be displayed at the index. If you don't have one yet, we will provide a default and you may upload yours later."))
    banner = forms.ImageField(required=False, help_text=_("This is the image that will be displayed at the event page, and is intended to be bigger than a cover. If you don't have one yet, we will provide a default and you may upload yours later."))
    image_disclaimer = forms.CharField( disabled=True, 
                                        widget=forms.Textarea(attrs={ 'rows': 3, 'cols': 10, 'style':'resize:none;'}), 
                                        label="", 
                                        initial=_("We would like to remind you that some images are copyrighted. We do not take responsibility for any copyright infrigements. The images will be deleted upon request of their rightful owner or their lawyers. Please, be aware of the rights you have over the image you want to upload before using it."))
    
    title = forms.CharField(required=True, label=_('Event Title'))
    description = forms.CharField(required=True, label=_('Description'), max_length=5000, widget=forms.Textarea) 
    
    city = forms.CharField(required=True, label=_('City'), max_length=100, help_text=_("In which city will this activity take place?"))

    start_date = forms.DateTimeField(required=True, label=_('Start date and time'), help_text=_("Example: 1984-11-15 19:25:36"))
    end_date = forms.DateTimeField(required=True, label=_('End date and time'), help_text=_("Example: 1984-11-15 19:25:36"))


    age_minimum = forms.IntegerField(required=True, label=_('Age minimum'), initial=18, help_text=_("Minimum age to attend this event."))

    show_title = forms.BooleanField(
                    required=False, 
                    label=_('Show the title?'), 
                    help_text=_("This is merely an aesthetic option. Maybe your banner already contains the event's title and you want to hide it?")
                )

    group_only_attendants = forms.BooleanField(
                    required=False, 
                    label=_('Is this a private event for your group?')
                )

    auto_register_users = forms.BooleanField(
                            required=False, 
                            label=_('Allow user auto-registration?'), 
                            help_text=_("Selected: Users join the group automatically. Not selected: Admins decide to accept or reject joining requests.")
                        )

    auto_register_activities = forms.BooleanField(
                            required=False, 
                            label=_('Allow activity auto-registration?'), 
                            help_text=_("Your group may have organize activities! Are members allowed to relate any of their activities to this group?")
                        )

    class Meta:
        model = Event
        fields = ("cover", "banner", "image_disclaimer", "title", "description", "city", "start_date", "end_date", "age_minimum", "show_title", "group_only_attendants", "auto_register_users", "auto_register_activities")
  

    def clean(self):
        super(EventForm, self).clean()
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if end_date < start_date:
            msg = _("The end date and time must be greater than the start date.")
            self._errors["end_date"] = self.error_class([msg])
            
        if self.instance is None and start_date <= timezone.now():
            msg = _("The start date and time must be greater than today's date.")
            self._errors["start_date"] = self.error_class([msg])
                
        elif start_date < self.instance.start_date and start_date < timezone.now():
            msg = _("You may bring forward the start date and time, but it must be greater than today's date.")
            self._errors["start_date"] = self.error_class([msg])

    def save_new(self, group):
        event = super(EventForm, self).save(commit=False)
        event.new(timezone.now(), group)  
        event.cover = self.cleaned_data["cover"]
        event.banner = self.cleaned_data["banner"]
        event.save()
        return event
        
    def save(self, commit=True):
        event = super(EventForm, self).save(commit=False)
        if commit:
            event.cover = self.cleaned_data["cover"]
            event.banner = self.cleaned_data["banner"]
            event.save()        
        return event  

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