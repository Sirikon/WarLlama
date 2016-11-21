import datetime

from django.test import TestCase
from django.utils import timezone

from .models import *


class SessionMethodTests(TestCase):

    ## HAS FINISHED
    def test_has_finished_with_past_date(self):
        """ 
        has_finished() should return True for sessions
        whose end_date are on the past
        """
        time = timezone.now() - datetime.timedelta(days=30)
        past_session = Session(start_date=time, end_date=time)
        self.assertIs(past_session.has_finished(), True)

    def test_has_finished_with_start_date_thirty_minutes_ago(self):
        """ 
        has_finished() should return True for sessions
        whose start_date were thirty minutes (or more) ago
        """
        time = timezone.now() - datetime.timedelta(minutes=30)
        present_session = Session(start_date=time, end_date=time)
        self.assertIs(present_session.has_finished(), True)

    def test_has_finished_with_now_start_date(self):
        """ 
        has_finished() should return False for sessions
        that start now
        """
        time = timezone.now()
        present_session = Session(start_date=time, end_date=time)
        self.assertIs(present_session.has_finished(), False)

    def test_has_finished_with_future_start_date(self):
        """ 
        has_finished() should return False for sessions
        with start_date in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_session = Session(start_date=time, end_date=time)
        self.assertIs(future_session.has_finished(), False)
    
    ## IS ON CONFIRMATION PERIOD 
    def test_is_on_confirmation_period_with_past_start_date(self):
        """ 
        is_on_confirmation_period() should return False for sessions
        with start_date in the past
        """
        time = timezone.now() - datetime.timedelta(days=30)

        fake_activity = Activity(confirmation_period=10)
        past_session = Session(activity=fake_activity, start_date=time, end_date=time)
        self.assertIs(past_session.is_on_confirmation_period(), False)
        
    def test_is_on_confirmation_period_with_present_start_date(self):
        """ 
        is_on_confirmation_period() should return True for sessions
        with start_date today
        """
        time = timezone.now()

        fake_activity = Activity(confirmation_period=10)
        present_session = Session(activity=fake_activity, start_date=time, end_date=time)
        self.assertIs(present_session.is_on_confirmation_period(), True)
        
    def test_is_on_confirmation_period_with_future_start_date_and_in_period_range(self):
        """ 
        is_on_confirmation_period() should return True for sessions
        with start_date in the future, and when less its confirmation_period,
        today's date is still on that range
        """
        time = timezone.now() + datetime.timedelta(days=5)

        fake_activity = Activity(confirmation_period=10)
        future_session = Session(activity=fake_activity, start_date=time, end_date=time)
        self.assertIs(future_session.is_on_confirmation_period(), True)
        
    def test_is_on_confirmation_period_with_future_start_date_and_not_in_period_range(self):
        """ 
        is_on_confirmation_period() should return True for sessions
        with start_date in the future, and when less its confirmation_period,
        today's date is not on that range
        """
        time = timezone.now() + datetime.timedelta(days=11)

        fake_activity = Activity(confirmation_period=10)
        future_session = Session(activity=fake_activity, start_date=time, end_date=time)
        self.assertIs(future_session.is_on_confirmation_period(), False)

    ## CAN USER JOIN    
    def test_can_user_join_user_is_author(self):
        """ 
        can_user_join() should return False if the user is the author
        of the activity
        """
        time = timezone.now()

        fake_user = User(username="Dummiedore")
        fake_user.save()
        
        fake_activity = Activity(author=fake_user, pub_date=time)
        fake_activity.save()

        fake_session = Session(activity=fake_activity, start_date=time, end_date=time)
        fake_session.save()

        self.assertIs(fake_session.can_user_join(fake_user), False)
        
    def test_can_user_join_user_is_not_attendant(self):
        """ 
        can_user_join() should return False if the user is not in
        the list of attendants of the activity
        """
        time = timezone.now()

        fake_author = User(username="Authorito")
        fake_author.save()
        fake_activity = Activity(pub_date=time, author=fake_author)
        fake_activity.save()
        fake_session = Session(activity=fake_activity, start_date=time, end_date=time)
        fake_session.save()
        
        fake_user = User(username="Dummiedore")
        fake_user.save()
        
        self.assertIs(fake_session.can_user_join(fake_user), False)
        
    def test_can_user_join_user_is_attendant_but_not_confirmed_attending_session(self):
        """ 
        can_user_join() should return True if the user is in
        the list of attendants of the activity and has not confirmed
        attending the session
        """
        time = timezone.now()

        fake_author = User(username="Authorito")
        fake_author.save()
        fake_activity = Activity(pub_date=time, author=fake_author)
        fake_activity.save()
        fake_session = Session(activity=fake_activity, start_date=time, end_date=time)
        fake_session.save()
        
        fake_user = User(username="Dummiedore")
        fake_user.save()

        fake_activity.attendants.add(fake_user)
        fake_activity.save()
        
        self.assertIs(fake_session.can_user_join(fake_user), True)
        
    def test_can_user_join_user_is_attendant_and_confirmed_attending_session(self):
        """ 
        can_user_join() should return False if the user is in
        the list of attendants of the activity and has confirmed
        attending the session
        """
        time = timezone.now()

        fake_author = User(username="Authorito")
        fake_author.save()
        fake_activity = Activity(pub_date=time, author=fake_author)
        fake_activity.save()
        fake_session = Session(activity=fake_activity, start_date=time, end_date=time)
        fake_session.save()
        
        fake_user = User(username="Dummiedore")
        fake_user.save()

        fake_activity.attendants.add(fake_user)
        fake_activity.save()

        fake_session.confirmed_attendants.add(fake_user)
        fake_session.save()
        
        self.assertIs(fake_session.can_user_join(fake_user), False)



        