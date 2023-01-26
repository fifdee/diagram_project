from django.db import models
from django.db.models.signals import post_save

from diagram.models import Subdivision, User
from diagram.text_choices import ACTIVITY_NAMES, DEFAULT_COLOR


# Create your models here.
class ActivityColor(models.Model):
    activity_name = models.CharField(max_length=30, verbose_name='aktywność')
    color_hex = models.CharField(max_length=7, verbose_name='kolor')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')

    def __str__(self):
        return f'{self.activity_name}; {self.color_hex}'


def set_default_colors(sender, instance, created, **kwargs):
    if created:
        for activity_name in ACTIVITY_NAMES:
            if activity_name[0] != '':
                ActivityColor.objects.create(activity_name=activity_name[1], color_hex=DEFAULT_COLOR[activity_name[0]],
                                             subdivision=instance.subdivision)


post_save.connect(set_default_colors, sender=User)
