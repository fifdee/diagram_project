import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save

from diagram.models import Subdivision, User
from diagram.text_choices import ACTIVITY_NAMES, DEFAULT_COLOR

from colorfield.fields import ColorField


class ActivityColor(models.Model):
    activity_name = models.CharField(max_length=30, verbose_name='aktywność')
    color_hex = ColorField(default='#FF0000', verbose_name='kolor')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')
    demo = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.activity_name}; {self.color_hex}; {self.subdivision}'

    def clean(self):
        super(ActivityColor, self).clean()

        r = re.match(r'#[a-fA-F0-9]{6}', self.color_hex)
        if not r:
            raise ValidationError({'color_hex': 'Provide correct hex color value.'})


def set_default_colors(sender, instance, created, **kwargs):
    print('launched set_default_colors')
    for activity_name in ACTIVITY_NAMES:
        if activity_name[0] != '' and instance is not None and instance.subdivision is not None:
            if ActivityColor.objects.filter(activity_name=activity_name[1],
                                            subdivision=instance.subdivision).count() == 0:
                ActivityColor.objects.create(activity_name=activity_name[1], color_hex=DEFAULT_COLOR[activity_name[0]],
                                             subdivision=instance.subdivision, demo=instance.subdivision.demo)


post_save.connect(set_default_colors, sender=User)
