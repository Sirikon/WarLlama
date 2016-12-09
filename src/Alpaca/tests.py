import datetime

from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import *

class ActivityMethodTests(TestCase):
    # GET_PAST_SESSIONS
    def test_get_past_sessions_no_sessions(self):
        """ 
        get_past_sessions() should return empty queryset
        if no sessions are past today
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        self.assertIs(the_activity.get_past_sessions().count() > 0, False)

    def test_get_past_sessions_only_one_past_session(self):
        """ 
        get_past_sessions() should return only one element
        in the queryset when there is only one past session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        time = timezone.now() - relativedelta(years=30)
        the_session = Session(activity=the_activity, start_date=time, end_date=time)
        the_session.save()

        past_session_list = the_activity.get_past_sessions()

        self.assertIs(past_session_list.count() == 1 and the_session in past_session_list, True)

    def test_get_past_sessions_only_past_sessions(self):
        """ 
        get_past_sessions() should return only one element
        in the queryset when there is only one past session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() - relativedelta(years=30)
        first_session = Session(activity=the_activity, start_date=time, end_date=time)
        first_session.save()

        time = timezone.now() - datetime.timedelta(days=30)
        second_session = Session(activity=the_activity, start_date=time, end_date=time)
        second_session.save()

        self.assertIs(the_activity.get_past_sessions().count() > 0, True)

    def test_get_past_sessions_both_past_future_sessions(self):
        """ 
        get_past_sessions() should return only one element
        in the queryset when there is only one past session,
        and not return the future session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() - relativedelta(years=30)
        past_session = Session(activity=the_activity, start_date=time, end_date=time)
        past_session.save()

        time = timezone.now() + datetime.timedelta(days=30)
        future_session = Session(activity=the_activity, start_date=time, end_date=time)
        future_session.save()

        past_session_list = the_activity.get_past_sessions()

        self.assertIs(past_session_list.count() == 1 and future_session not in past_session_list, True)

    # GET_FUTURE_SESSIONS
    def test_get_future_sessions_no_sessions(self):
        """ 
        get_future_sessions() should return empty queryset
        if no sessions happen after today
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        self.assertIs(the_activity.get_future_sessions().count() > 0, False)

    def test_get_future_sessions_only_one_future_session(self):
        """ 
        get_future_sessions() should return only one element
        in the queryset when there is only one future session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        time = timezone.now() + relativedelta(years=30)
        the_session = Session(activity=the_activity, start_date=time, end_date=time)
        the_session.save()

        future_session_list = the_activity.get_future_sessions()

        self.assertIs(future_session_list.count() == 1 and the_session in future_session_list, True)

    def test_get_future_sessions_only_future_sessions(self):
        """ 
        get_future_sessions() should return only one element
        in the queryset when there is only one future session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() + relativedelta(years=30)
        first_session = Session(activity=the_activity, start_date=time, end_date=time)
        first_session.save()

        time = timezone.now() + datetime.timedelta(days=30)
        second_session = Session(activity=the_activity, start_date=time, end_date=time)
        second_session.save()

        self.assertIs(the_activity.get_future_sessions().count() > 0, True)

    def test_get_past_sessions_both_past_future_sessions(self):
        """ 
        get_past_sessions() should return only one element
        in the queryset when there is only one future session,
        and not return the past session
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() - relativedelta(years=30)
        past_session = Session(activity=the_activity, start_date=time, end_date=time)
        past_session.save()

        time = timezone.now() + datetime.timedelta(days=30)
        future_session = Session(activity=the_activity, start_date=time, end_date=time)
        future_session.save()

        future_session_list = the_activity.get_future_sessions()

        self.assertIs(future_session_list.count() == 1 and past_session not in future_session_list, True)

    # GET_NEXT_SESSION
    def test_get_next_session_no_sessions(self):
        """ 
        get_next_session() should return None if no sessions
        happen after today
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        self.assertIs(the_activity.get_next_session(), None)

    def test_get_next_session_only_past_sessions(self):
        """ 
        get_next_session() should return None if no sessions
        happen after today
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() - relativedelta(years=30)
        first_session = Session(activity=the_activity, start_date=time, end_date=time)
        first_session.save()

        time = timezone.now() - datetime.timedelta(days=30)
        second_session = Session(activity=the_activity, start_date=time, end_date=time)
        second_session.save()

        self.assertIs(the_activity.get_next_session(), None)


    def test_get_next_session_one_future_session(self):
        """ 
        get_next_session() should return the only future
        session there is
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()
        
        time = timezone.now() - relativedelta(years=30)
        first_session = Session(activity=the_activity, start_date=time, end_date=time)
        first_session.save()

        time = timezone.now() - datetime.timedelta(days=30)
        second_session = Session(activity=the_activity, start_date=time, end_date=time)
        second_session.save()

        time = timezone.now() + datetime.timedelta(days=30)
        future_session = Session(activity=the_activity, start_date=time, end_date=time)
        future_session.save()

        self.assertIs(the_activity.get_next_session().id, future_session.id)


    def test_get_next_session_multilple_future_session(self):
        """ 
        get_next_session() should return the first future
        session there is
        """
        the_author = User(username="", password="", email="")
        the_author.save()
        the_activity = Activity(pub_date=timezone.now(), author=the_author)
        the_activity.save()

        time = timezone.now() + relativedelta(years=30)
        future_session = Session(activity=the_activity, start_date=time, end_date=time)
        future_session.save()
        
        time = timezone.now() - datetime.timedelta(days=30)
        past_session = Session(activity=the_activity, start_date=time, end_date=time)
        past_session.save()
        
        time = timezone.now() + datetime.timedelta(days=3)
        next_session = Session(activity=the_activity, start_date=time, end_date=time)
        next_session.save()

        self.assertIs(the_activity.get_next_session().id, next_session.id)

    # IS USER OLD ENOUGH
    def test_is_user_old_enough_over_minimum_age(self):
        """ 
        is_user_old_enough() should return True for users
        whose age is over the minimum age of the activity
        """
        date = timezone.now() - relativedelta(years=30)
        old_user = User(username="")
        profile = Profile(user=old_user, birth_date=date)

        the_activity = Activity(age_minimum=18)
        self.assertIs(the_activity.is_user_old_enough(old_user), True)

    def test_is_user_old_enough_exact_minimum_age(self):
        """ 
        is_user_old_enough() should return True for users
        whose age is equal to the minimum age of the activity
        """
        date = timezone.now() - relativedelta(years=18)
        the_user = User(username="")
        profile = Profile(user=the_user, birth_date=date)

        the_activity = Activity(age_minimum=18)
        self.assertIs(the_activity.is_user_old_enough(the_user), True)

    def test_is_user_old_enough_under_minimum_age(self):
        """ 
        is_user_old_enough() should return False for users
        whose age is under the minimum age of the activity
        """
        date = timezone.now() - relativedelta(years=5)
        young_user = User(username="")
        profile = Profile(user=young_user, birth_date=date)

        the_activity = Activity(age_minimum=18)
        self.assertIs(the_activity.is_user_old_enough(young_user), False)


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



        