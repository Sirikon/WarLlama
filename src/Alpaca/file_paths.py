
    
import random

def user_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/avatar
    return 'user_{0}/{1}'.format(str(instance.user.id), "avatar." + filename.rsplit('.', 1)[1])
    
def group_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/avatar
    return 'group_{0}/{1}'.format(str(instance.id), "logo." + filename.rsplit('.', 1)[1])
    
def activity_cover_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/avatar
    return 'user_{0}/{1}/{2}'.format(str(instance.author.id), "activities", str(instance.id) + "cover." + filename.rsplit('.', 1)[1])

def activity_no_cover_path():
    alpaquitas = ["Zero", "Branding", "Reversed", "Dark"]
    lucky_one = random.randint(0, len(alpaquitas) - 1)
    return "web/activities/Al-Paquita_{0}.png".format(alpaquitas[lucky_one])
