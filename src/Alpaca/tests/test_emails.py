import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ..models import *
from ..emails import *


class EmailLanguageTests(TestCase):

    def test_english_emails(self):
        """ 
        all emails must return True
        """
        time = timezone.now()
        date = timezone.now() - relativedelta(years=5)

        
        author = User(username="Authorito") 
        author.save()
        author_profile = Profile(user=author, birth_date=date)  
        author_profile.save()

        attendant = User(username="Dummiedore")  
        attendant.save()
        attendant_profile = Profile(user=attendant, birth_date=date, language_preference="en")  
        attendant_profile.save()

        activity = Activity(pub_date=time, author=author)
        activity.save()
        activity.attendants.add(attendant)   
        activity.save()

        session = Session(activity=activity, start_date=time, end_date=time)    
        session.save()

        session.confirmed_attendants.add(attendant)      
        session.save()
        
        self.assertIs(email_confirm_account(attendant), True)
        self.assertIs(email_reset_password(attendant), True)

        self.assertIs(email_registered_your_new_activity(activity), True)

        self.assertIs(email_user_acted_on_your_activity(activity, attendant, True), True)
        self.assertIs(email_user_acted_on_your_activity(activity, attendant, False), True)

        self.assertIs(email_user_requested_to_join(activity, attendant), True)
        self.assertIs(email_user_confirmed_assistance(activity, session, attendant), True)

        self.assertIs(email_you_were_kicked_out_from_activity(activity, attendant), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, True), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, False), True)
        self.assertIs(email_activity_got_updated(activity, attendant), True)
        self.assertIs(email_activity_new_sessions(activity, attendant), True)
        self.assertIs(email_confirm_assistance_period_started(activity, session, attendant), True)

        

    def test_spanish_emails(self):
        """ 
        all emails must return True
        """
        time = timezone.now()
        date = timezone.now() - relativedelta(years=5)

        
        author = User(username="Authorito") 
        author.save()
        author_profile = Profile(user=author, birth_date=date)  
        author_profile.save()

        attendant = User(username="Dummiedore")  
        attendant.save()
        attendant_profile = Profile(user=attendant, birth_date=date, language_preference="es")  
        attendant_profile.save()

        activity = Activity(pub_date=time, author=author)
        activity.save()
        activity.attendants.add(attendant)   
        activity.save()

        session = Session(activity=activity, start_date=time, end_date=time)    
        session.save()

        session.confirmed_attendants.add(attendant)      
        session.save()
        
        self.assertIs(email_confirm_account(attendant), True)
        self.assertIs(email_reset_password(attendant), True)

        self.assertIs(email_registered_your_new_activity(activity), True)

        self.assertIs(email_user_acted_on_your_activity(activity, attendant, True), True)
        self.assertIs(email_user_acted_on_your_activity(activity, attendant, False), True)

        self.assertIs(email_user_requested_to_join(activity, attendant), True)
        self.assertIs(email_user_confirmed_assistance(activity, session, attendant), True)

        self.assertIs(email_you_were_kicked_out_from_activity(activity, attendant), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, True), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, False), True)
        self.assertIs(email_activity_got_updated(activity, attendant), True)
        self.assertIs(email_activity_new_sessions(activity, attendant), True)
        self.assertIs(email_confirm_assistance_period_started(activity, session, attendant), True)


    def test_euskera_emails(self):
        """ 
        all emails must return True
        """
        time = timezone.now()
        date = timezone.now() - relativedelta(years=5)

        
        author = User(username="Authorito") 
        author.save()
        author_profile = Profile(user=author, birth_date=date)  
        author_profile.save()

        attendant = User(username="Dummiedore")  
        attendant.save()
        attendant_profile = Profile(user=attendant, birth_date=date, language_preference="eus")  
        attendant_profile.save()

        activity = Activity(pub_date=time, author=author)
        activity.save()
        activity.attendants.add(attendant)   
        activity.save()

        session = Session(activity=activity, start_date=time, end_date=time)    
        session.save()

        session.confirmed_attendants.add(attendant)      
        session.save()
        
        self.assertIs(email_confirm_account(attendant), True)
        self.assertIs(email_reset_password(attendant), True)

        self.assertIs(email_registered_your_new_activity(activity), True)

        self.assertIs(email_user_acted_on_your_activity(activity, attendant, True), True)
        self.assertIs(email_user_acted_on_your_activity(activity, attendant, False), True)

        self.assertIs(email_user_requested_to_join(activity, attendant), True)
        self.assertIs(email_user_confirmed_assistance(activity, session, attendant), True)

        self.assertIs(email_you_were_kicked_out_from_activity(activity, attendant), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, True), True)
        self.assertIs(email_your_request_was_handled(activity, attendant, False), True)
        self.assertIs(email_activity_got_updated(activity, attendant), True)
        self.assertIs(email_activity_new_sessions(activity, attendant), True)
        self.assertIs(email_confirm_assistance_period_started(activity, session, attendant), True)

        