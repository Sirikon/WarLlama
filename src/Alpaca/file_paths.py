   
import random

# file will be uploaded to MEDIA_ROOT/user_<id>/avatar

# -- UPLOAD PATHS
def user_avatar_path(instance, filename):    
    return 'user_{0}/{1}'.format(str(instance.user.id), "avatar." + filename.rsplit('.', 1)[1])
    
def group_logo_path(instance, filename):
    return 'group_{0}/{1}'.format(str(instance.id), "logo." + filename.rsplit('.', 1)[1])
    
def activity_cover_path(instance, filename):
    return 'user_{0}/{1}/{2}'.format(str(instance.author.id), "activities", str(instance.id) + "cover." + filename.rsplit('.', 1)[1])

def event_cover_path(instance, filename):
    return 'group_{0}/{1}/{2}'.format(str(instance.group.id), "events", str(instance.id) + "cover." + filename.rsplit('.', 1)[1])
    
def event_banner_path(instance, filename):
    return 'group_{0}/{1}/{2}'.format(str(instance.group.id), "events", str(instance.id) + "banner." + filename.rsplit('.', 1)[1])

# -- NO IMAGE PATHS
def no_cover_path():
    alpaquitas = ["Zero", "Branding", "Reversed", "Dark"]
    lucky_one = random.randint(0, len(alpaquitas) - 1)
    return "web/activities/Al-Paquita_{0}.png".format(alpaquitas[lucky_one])
    
def event_no_banner_path():
    alpaquitas = ["Zero", "Branding", "Reversed", "Dark"]
    lucky_one = random.randint(0, len(alpaquitas) - 1)
    return "web/activities/Al-Paquita_{0}.png".format(alpaquitas[lucky_one])
