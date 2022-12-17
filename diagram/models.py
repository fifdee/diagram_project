from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save, post_save

from diagram.text_choices import ranks, activity_names
from diagram.utilities import activity_conflicts, merge_neighbour_activities


class User(AbstractUser):
    subdivision = models.ForeignKey('Subdivision', on_delete=models.SET_NULL, null=True, verbose_name='pododdział')


class Subdivision(models.Model):
    name = models.CharField(max_length=30, verbose_name='nazwa')

    def __str__(self):
        return self.name


class Soldier(models.Model):
    rank = models.CharField(max_length=20, choices=ranks, verbose_name='stopień')
    first_name = models.CharField(max_length=20, verbose_name='imię')
    last_name = models.CharField(max_length=30, verbose_name='nazwisko')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')
    position = models.CharField(max_length=30, verbose_name='stanowisko', null=True, blank=True)
    personal_number = models.IntegerField(verbose_name='PESEL', null=True, blank=True)
    father_name = models.CharField(max_length=30, verbose_name='imię ojca', null=True, blank=True)
    id_card_number = models.CharField(max_length=30, verbose_name='nr leg. służb.', null=True, blank=True)
    driving_license = models.CharField(max_length=30, verbose_name='kat. prawa jazdy', null=True, blank=True)

    def __str__(self):
        return f'{self.rank} {self.first_name} {self.last_name} ({self.subdivision})'


class Activity(models.Model):
    soldier = models.ForeignKey(Soldier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='żołnierz')
    name = models.CharField(max_length=30, choices=activity_names, verbose_name='nazwa')
    description = models.CharField(max_length=200, default='', blank=True, verbose_name='opis')
    start_date = models.DateField(verbose_name='data rozpoczęcia')
    end_date = models.DateField(verbose_name='data zakończenia')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')

    def clean(self):
        super(Activity, self).clean()

        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'data zakończenia nie może być przed datą rozpoczęcia'})

        # validation for specific soldier's activities
        if self.soldier:
            conflict = activity_conflicts(self, Activity)
            if conflict:
                raise ValidationError(
                    f'Wybrane daty rozpoczęcia i zakończenia nakładają się z inną aktywnością: {conflict["name"]} '
                    f'(data rozpoczęcia: {conflict["start_date"]}, data zakończenia: {conflict["end_date"]})')

    def __str__(self):
        return f'{self.name} {self.description} ({self.soldier})'


def launch_merge_neighbour_activities(sender, instance, **kwargs):
    merge_neighbour_activities(instance)


post_save.connect(launch_merge_neighbour_activities, sender=Activity)


def set_username(sender, instance, **kwargs):
    email = instance.email
    username = email[:30]
    n = 1
    while User.objects.exclude(pk=instance.pk).filter(username=username).exists():
        n += 1
        username = email[:(29 - len(str(n)))] + '-' + str(n)
    instance.username = username


pre_save.connect(set_username, sender=User)
