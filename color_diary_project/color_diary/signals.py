from django.db.models.signals import post_save
from .models import Color, User
from .fields import parse_hex_color


def default_color_setting(sender, instance, created, **kwargs):
    default_color = Color.get_default_color()
    hex_color_list = [
        'D75674',
        'F7774D',
        'F9BB2B',
        'B7BF19',
        '00A583',
        '008FB3',
        '4D73BB',
        '9C5DA0',
    ]
    for hex_color in hex_color_list:
        color = Color.objects.create(hex_color=parse_hex_color(hex_color))
        color.users.add(instance)
        color.save()

    if created:
        default_color.users.add(instance)
        default_color.save()


post_save.connect(receiver=default_color_setting, sender=User, dispatch_uid='default_color_setting', weak=False)
