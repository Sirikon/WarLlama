import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ..models import *

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
