from django.db.models import Count, Q

from django.utils import translation
from django import http
from django.conf import settings

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language
from django.core.mail import EmailMessage

from ..models import *
from .utils import set_translation

def email_signature():
    # Translators: This is the signing part of an email. 
    return "<br/><br/>" + str(_("Always watching over you,")) + "<br/>" + str(_("Big Evil Llama"))

# USERs
def email_confirm_account(link, new_user):
    # Subject: Alpaca: Confirm your account
    # Body: 
    # Hi!
    #
    # I'm the Big Evil Llama. I watch over every activity in my land, http://alpaca.srk.bz
    # 
    # It seems like you wanted to become one of my alpacas! If it is so, be welcomed! You can confirm your account by clicking the following link:
    # [Link]
    #
    # If it wasn't you who created this account, you can just ignore this email.
    #
    # Alpaca hugs!
    # Big Evil Llama

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(new_user.profile.language_preference)

    subject = str(_("Alpaca: Confirm your account"))
    body = str(_("Hi!")) + "<br/><br/>" + str(_("I'm the Big Evil Llama. I watch over every activity in my land")) + ", http://alpaca.srk.bz" + "<br/><br/>" + str(_("It seems like you wanted to become one of my alpacas! If it is so, be welcomed! You can confirm your account by clicking the following link:")) + link + "<br/><br/>" + str(_("If it wasn't you who created this account, you can just ignore this email.")) + "<br/><br/>" + str(_("Alpaca hugs!")) + "<br/>" + str(_("Big Evil Llama"))

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [new_user.email])
    msg.content_subtype = "html"
    msg.send()



# AUTHORs
def email_registered_your_new_activity(activity):
    # Subject: Your Activity "[Title]" was succesfully registered!
    # Body:
    # Hi, [Author]!
    #
    # Your activity "[Title]" has been succesfully registered, and you may start sharing it by using the following link:
    # http://alpaca.srk.bz/activity/[id]
    #
    # Your activity may not appear on the main page index until some time has passed, but it is already fully functional.
    #
    # Have fun! I hope everything goes as you expect it <3
    # 
    # Always watching over you,
    # Big Evil Llama
    
    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(activity.author.profile.language_preference)

    subject = _('Your Activity "') + activity.title + _('" was succesfully registered!')

    body = str(_("Hi, ")) + activity.author.username + "<br/><br/>" + str(_('Your activity "')) + activity.title + str(_('" has been succesfully registered, and you may start sharing it by using the following link:')) + "<br/>http://alpaca.srk.bz/activity/" + str(activity.id) + "<br/><br/>" + str(_("Your activity may not appear on the main page index until some time has passed, but it is already fully functional.")) + "<br/><br/>" + str(_( "Have fun! I hope everything goes as you expect it <3")) + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [activity.author.email])
    msg.content_subtype = "html"
    msg.send()



def email_user_acted_on_your_activity(activity, attendant, has_joined):
    # Subject: [username] joined/left [title]
    # Body:
    # Hi, [author]!
    #
    # [Username] has joined/left your activity, [title].
    # You can manage your activity at http://alpaca.srk.bz/activity/[id]
    # 
    # Always watching over you,
    # Big Evil Llama
    
    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(activity.author.profile.language_preference)

    aux = str(_("joined"))
    if not has_joined:
        aux = str(_("left"))

    subject = attendant.username + str(_(" has ")) + aux + str(_(" your activity, ")) + activity.title
    body = str(_("Hi, ")) + activity.author.username + "<br/><br/>" + attendant.username + str(_(" has ")) + aux + str(_(" your activity, ")) + activity.title + "." + "<br/><br/>" + str(_("You can manage your activity at ")) + "http://alpaca.srk.bz/activity/" + str(activity.id) + email_signature()
    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [activity.author.email])
    msg.content_subtype = "html"
    msg.send()


def email_user_requested_to_join(activity, attendant):
    # Subject: [username] requested to join [title]!
    # Body:
    # Hi, [author]!
    #
    # [Username] has requested to join your activity, [title].
    # You can manage this and any other requests at http://alpaca.srk.bz/activity/[id]
    # 
    # Always watching over you,
    # Big Evil Llama
    
    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(activity.author.profile.language_preference)

    subject = attendant.username + str(_(" requested to join ")) + activity.title
    body = str(_("Hi, ")) + activity.author.username + "<br/><br/>" + attendant.username + str(_(" has requested to join your activity, ")) + activity.title + "." + "<br/>" + str(_("You can manage this and any other requests at ")) + "http://alpaca.srk.bz/activity/" + str(activity.id)  + email_signature()
    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [activity.author.email])
    msg.content_subtype = "html"
    msg.send()


def email_user_confirmed_assistance(activity, session, attendant):
    # Subject: [username] confirmed assistance on your activity, [title]
    # Body:
    # Hi, [author]!
    #
    # Congratulations! [username] has confirmed assistance to the [date]'s session!
    # You can manage your activity at http://alpaca.srk.bz/activity/[id]
    #
    # I hope everything goes as you expect it <3
    # 
    # Always watching over you,
    # Big Evil Llama

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(activity.author.profile.language_preference)
    
    subject = attendant.username + str(_(" confirmed assistance on your activity, ")) + activity.title
    body =  str(_("Hi, ")) + activity.author.username + "<br/><br/>" + str(_("Congratulations! ")) + attendant.username + str(_(" has confirmed assistance to the ")) + session.datetime.date + str(_("'s session!'")) + "<br/>" + str(_("You can manage your activity at")) + "http://alpaca.srk.bz/activity/" + str(activity.id) + "<br/><br/>" + str(_("I hope everything goes as you expect it <3")) + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [activity.author.email])
    msg.content_subtype = "html"
    msg.send()

# ATTENDANTs
def email_you_were_kicked_out_from_activity(activity, attendant):
    # Subject: You have been removed from the activity [Title]
    # Body:
    # Hi, [username],
    #
    # I regret to inform you that you have been removed from the activity [title].
    #
    # However, don't forget there are many other activities waiting for you at http://alpaca.srk.bz!
    # 
    # Always watching over you,
    # Big Evil Llama
    
    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(attendant.profile.language_preference)

    subject = str(_("You have been removed from the activity ")) + activity.title
    body = str(_("Hi, ")) + attendant.username + "," + "<br/><br/>" + str(_("I regret to inform you that you have been removed from the activity ")) + activity.title + "." + "<br/><br/>" + str(_("However, don't forget there are many other activities waiting for you at ")) + "http://alpaca.srk.bz!" + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [attendant.email])
    msg.content_subtype = "html"
    msg.send()
    

def email_your_request_was_handled(activity, attendant, was_accepted):
    # Subject: Accepted/Rejected request to join the activity "[title]"
    # Body:
    # Hi, [username]!
    #
    # Your request to join the activity "[Title]" has been accepted/Rejected.
    #
    # Don't forget there are many other activities waiting for you at http://alpaca.srk.bz!
    # 
    # Always watching over you,
    # Big Evil Llama

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(attendant.profile.language_preference)

    aux = str(_("accepted"))
    if not was_accepted:
        aux = str(_("rejected"))

    subject = aux[:1].upper() + aux[1:] + str(_(" request to join the activity ")) + activity.title
    body = str(_("Hi, ")) + attendant.username + "<br/><br/>" + str(_("Your request to join the activity ")) + activity.title + str(_(" has been ")) + aux + "." + "<br/><br/>" + str(_("Don't forget there are many other activities waiting for you at ")) + "http://alpaca.srk.bz!" + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [attendant.email])
    msg.content_subtype = "html"
    msg.send()
    

def email_activity_got_updated(activity, attendant):
    # Subject: Updated: Activity [Title]!
    # Body:
    # Hi, [username]! 
    #
    # You are receiving this message because the activity [title] was updated!
    #
    # Check it out at http://alpaca.srk.bz/activity/[id]!
    # 
    # Always watching over you,
    # Big Evil Llama

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.

    translation.activate(attendant.profile.language_preference)

    subject = str(_("Updated: Activity ")) + activity.title
    body = str(_("Hi, ")) + attendant.username + "<br/><br/>" + str(_("You are receiving this message because the activity ")) + activity.title + str(_(" was updated!")) + "<br/><br/>" + str(_("Check it out at ")) + "http://alpaca.srk.bz/activity/" + str(activity.id) + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [attendant.email])
    msg.content_subtype = "html"
    msg.send()


def email_activity_new_sessions(activity, attendant):
    # Subject: New Sessions in Activity [Title]
    # Body:
    # Hi, [username]! 
    #
    # You are receiving this message because the activity [title] was updated with new sessions!
    #
    # Check them out at http://alpaca.srk.bz/activity/[id]! Hope to see you there <3
    # 
    # Always watching over you,
    # Big Evil Llama

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(attendant.profile.language_preference)

    subject = str(_("New Session in Activity ")) + activity.title
    body = str(_("Hi, ")) + attendant.username + "<br/><br/>" + str(_("You are receiving this message because the activity ")) + activity.title + str(_(" was updated with new sessions!")) + "<br/><br/>" + str(_("Check them out at")) + "http://alpaca.srk.bz/activity/" + str(activity.id) + str(_(" Hope to see you there <3")) + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [attendant.email])
    msg.content_subtype = "html"
    msg.send()


def email_confirm_assistance_period_started(activity, session, attendant):
    # Subject: You can confirm your assistance!
    # Body:
    # Hi, [username]!
    #
    # The activity [Title] is requesting attending users to confirm their assistance to [date]'s session! You may do so by going to the activity's page: 
    # http://alpaca.srk.bz/activity/[id]!
    #
    # We hope to see you there <3
    #
    # Always watching over you,
    # Big Evil Llama
    
    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(attendant.profile.language_preference)
    
    subject = str(_("You can confirm your assistance!"))
    body = str(_("Hi, ")) + attendant.username + "<br/><br/>" + str(_("The activity ")) + activity.title + str(_(" is requesting attending users to confirm their assistance to ")) + session.datetime.date + str(_("'s session! You may do so by going to the activity's page:")) + "<br/>" + "http://alpaca.srk.bz/activity/" + str(activity.id) + "<br/><br/>" + str(_("We hope to see you there <3")) + email_signature()

    msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [attendant.email])
    msg.content_subtype = "html"
    msg.send()


