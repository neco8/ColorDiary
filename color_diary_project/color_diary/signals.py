from django.db.models.signals import post_save
from .models import Color, User


def default_color_setting(sender, instance, created, **kwargs):
    default_color = Color.get_default_color()

    if created:
        default_color.users.add(instance)
        default_color.save()


post_save.connect(receiver=default_color_setting, sender=User, dispatch_uid='default_color_setting', weak=False)
