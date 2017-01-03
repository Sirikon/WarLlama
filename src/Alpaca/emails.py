#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Count, Q

from django.utils import translation
from django import http
from django.conf import settings

from django.utils.translation import ugettext_lazy as _ ## For Multi-Language
from django.core.mail import EmailMessage

from utils import set_translation

def send_my_email(subject, body, to_whom):
    try:
        msg = EmailMessage(subject, body, 'noreply@alpaca.srk.bz', [to_whom])
        msg.content_subtype = "html"
        msg.send()
    except Exception as e:
        print e
        return False
    
    return True


def email_signature():
    # Translators: This is the signing part of an email. 
    return "<br/><br/>" + str(_("Always watching over you,")) + "<br/>" + str(_("Big Evil Llama"))

# USERs
def email_confirm_account(new_user):
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
    body = str(_("Hi!{newline}I'm the Big Evil Llama. I watch over every activity in my land, {alpaca_link}.{newline}It seems like you wanted to become one of my alpacas! If it is so, be welcomed! You can confirm your account by clicking the following link: {confirmation_link}.{newline}If it wasn't you who created this account, you can just ignore this email.{newline}Alpaca hugs!{jumpline}Big Evil Llama"))

    link = "http://alpaca.srk.bz/activate?email=" + new_user.email + "&token=" + new_user.profile.current_token

    body = body.format(jumpline = "<br/>", newline="<br/><br/>", alpaca_link="https://alpaca.srk.bz", confirmation_link=link)

    return send_my_email(subject, body, new_user.email)


def email_reset_password(user):
    # Subject: Alpaca: Confirm your account
    # Body: 
    # Hi, [user]!
    #
    # You are receiving this message because you forgot your password and asked for a new one.
    # You may do so by clicking the following link and the instructions there:
    # [Link]
    #
    # If it wasn't you asked for a new password, you can just ignore this email.
    #
    # [Signature]

    # Translators: This is an e-mail. Some sentences may be cut due to the site's necesities. Please, read all parts before translating them, so every punctuation mark is correct. There may be spaces before or after some sentences, include them. You may ask the admin of the site for a copy of the e-mail, should you need it.
    
    translation.activate(user.profile.language_preference)

    subject = str(_("Alpaca: Reset your password"))
    body = str(_("Hi, {username}!{newline}You are receiving this message because you forgot your password and asked for a new one.{jumpline}You may do so by clicking the following link and the instructions there:{jumpline}{reset_link}{newline}If it wasn't you asked for a new password, you can just ignore this email.{email_signature}"))

    link = "http://alpaca.srk.bz/resetpassword?email=" + user.email + "&token=" + user.profile.current_token
    body = body.format( jumpline="<br/>",
                        newline="<br/><br/>", 
                        username=user.username,
                        reset_link=link, 
                        email_signature=email_signature())

    return send_my_email(subject, body, user.email)



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

    subject = str(_('Your Activity "')) + activity.title.encode("utf8") + str(_('" was succesfully registered!'))
    body = str(_("Hi, {author}!{newline}Your activity \"{title}\" has been succesfully registered, and you may start sharing it by using the following link: {activity_link}.{newline}Your activity may not appear on the main page index until some time has passed, but it is already fully functional.{newline}Have fun! I hope everything goes as you expect it <3 {email_signature}"))

    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format( newline="<br/><br/>", 
                        author=activity.author.username, 
                        title=activity.title.encode("utf8"), 
                        activity_link=link, 
                        email_signature=email_signature())

    return send_my_email(subject, body, activity.author.email)


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

    subject = str(attendant.username) + str(_(" has ")) + str(aux) + str(_(" your activity, ")) + activity.title.encode("utf8")
    body = str(_("Hi, {author}!{newline}{attendant} has {action} your activity, {title}.{jumpline}You can manage your activity at {activity_link}.{email_signature}"))
    
    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format(jumpline="<br/>", newline="<br/><br/>", 
                action=aux,
                author=activity.author.username, attendant=attendant.username,
                title=activity.title.encode("utf8"), activity_link=link, 
                email_signature=email_signature())

    return send_my_email(subject, body, activity.author.email)


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

    subject = str(attendant.username) + str(_(" requested to join ")) + activity.title.encode("utf8")
    body = str(_("Hi, {author}!{newline}{attendant} has requested to join your activity, {title}.{jumpline}You can manage this and any other requests at {activity_link}.{email_signature}"))
    
    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format(jumpline="<br/>", newline="<br/><br/>", 
                author=activity.author.username, attendant=attendant.username,
                title=activity.title.encode("utf8"), activity_link=link, 
                email_signature=email_signature())
    return send_my_email(subject, body, activity.author.email)


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
    
    subject = str(attendant.username) + str(_(" confirmed assistance on your activity, ")) + activity.title.encode("utf8")
    body =  str(_("Hi, {author}!{newline}Congratulations! {attendant} has confirmed assistance to the {date}'s session!{jumpline}You can manage your activity at {activity_link}.{newline}I hope everything goes as you expect it <3 {email_signature}"))

    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format( jumpline="<br/>", newline="<br/><br/>", 
                        author=activity.author.username, attendant=attendant.username,
                        date=session.start_date.date(), activity_link=link, 
                        email_signature=email_signature())

    return send_my_email(subject, body, activity.author.email)

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

    subject = str(_("You have been removed from the activity ")) + activity.title.encode("utf8")
    body = str(_("Hi, {attendant},{newline}I regret to inform you that you have been removed from the activity {title}.{newline}However, don't forget there are many other activities waiting for you at {alpaca_link}.{email_signature}"))

    link = "http://alpaca.srk.bz"
    body = body.format( jumpline="<br/>", newline="<br/><br/>", 
                        attendant=attendant.username,
                        title=activity.title.encode("utf8"), 
                        alpaca_link=link, 
                        email_signature=email_signature())
    return send_my_email(subject, body, attendant.email)
    

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

    subject = str(aux[:1].upper() + aux[1:]) + str(_(" request to join the activity ")) + activity.title.encode("utf8")
    body = str(_("Hi, {attendant},{newline}Your request to join the activity {title} has been {action}.{newline}Don't forget there are many other activities waiting for you at {alpaca_link}.{email_signature}"))

    link = "http://alpaca.srk.bz"
    body = body.format( newline="<br/><br/>", 
                        attendant=attendant.username,
                        action=aux,
                        title=activity.title.encode("utf8"), 
                        alpaca_link=link, 
                        email_signature=email_signature())

    return send_my_email(subject, body, attendant.email)
    

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

    subject = str(_("Updated: Activity ")) + activity.title.encode("utf8")
    body = str(_("Hi, {attendant}!{newline}You are receiving this message because the activity {title} was updated!{newline}Check it out at {activity_link}.{email_signature}"))

    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format( newline="<br/><br/>", 
                        attendant=attendant.username,
                        title=activity.title.encode("utf8"), 
                        activity_link=link, 
                        email_signature=email_signature())

    return send_my_email(subject, body, attendant.email)


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

    subject = str(_("New Session in Activity ")) + activity.title.encode("utf8")
    body = str(_("Hi, {attendant}!{newline}You are receiving this message because the activity {title} was updated with new sessions!{newline}Check them out at {activity_link}.{newline}Hope to see you there <3{email_signature}"))
    
    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format( newline="<br/><br/>", 
                        attendant=attendant.username,
                        title=activity.title.encode("utf8"), 
                        activity_link=link, 
                        email_signature=email_signature())
    return send_my_email(subject, body, attendant.email)


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
    body = str(_("Hi, {attendant}!{newline}The activity {title} is requesting attending users to confirm their assistance to {date}'s session! You may do so by going to the activity's page:{activity_link}.{newline}We hope to see you there <3 {email_signature}"))

    link = "http://alpaca.srk.bz/activity/" + str(activity.id)
    body = body.format( newline="<br/><br/>", 
                        attendant=attendant.username,
                        title=activity.title.encode("utf8"), date=session.start_date.date(),
                        activity_link=link, 
                        email_signature=email_signature())
    return send_my_email(subject, body, attendant.email)


