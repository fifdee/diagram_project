from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save, post_save

from diagram.text_choices import RANKS, ACTIVITY_NAMES, DEFAULT_SOLDIER_INFO, EVERYDAY_ACTIVITY_NAMES
from diagram.functions import activity_conflicts, merge_neighbour_activities, assign_if_check_passed, \
    everyday_activity_conflicts, validate_how_many_everyday_activities


class User(AbstractUser):
    subdivision = models.ForeignKey('Subdivision', on_delete=models.SET_NULL, null=True, verbose_name='pododdział')


class Subdivision(models.Model):
    name = models.CharField(max_length=30, verbose_name='nazwa')

    def __str__(self):
        return self.name


class Soldier(models.Model):
    rank = models.CharField(max_length=20, choices=RANKS, verbose_name='stopień')
    first_name = models.CharField(max_length=20, verbose_name='imię')
    last_name = models.CharField(max_length=30, verbose_name='nazwisko')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')

    def __str__(self):
        return f'{self.rank} {self.first_name} {self.last_name} ({self.subdivision})'


class SoldierInfo(models.Model):
    soldier = models.ForeignKey(Soldier, on_delete=models.CASCADE, verbose_name='żołnierz')
    name = models.CharField(max_length=20, verbose_name='nazwa')
    value = models.CharField(max_length=30, default='')


class Activity(models.Model):
    soldier = models.ForeignKey(Soldier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='żołnierz')
    name = models.CharField(max_length=30, choices=ACTIVITY_NAMES, verbose_name='nazwa')
    description = models.CharField(max_length=200, default='', blank=True, verbose_name='opis')
    start_date = models.DateField(verbose_name='data rozpoczęcia')
    end_date = models.DateField(verbose_name='data zakończenia', blank=True)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')

    def clean(self):
        super(Activity, self).clean()

        if self.start_date and not self.end_date:
            self.end_date = self.start_date

        if self.end_date and self.start_date:
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


class EverydayActivity(models.Model):
    name = models.CharField(max_length=30, choices=EVERYDAY_ACTIVITY_NAMES, verbose_name='nazwa')
    how_many = models.IntegerField(verbose_name='ile dziennie', default=1, validators=[validate_how_many_everyday_activities])
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='pododdział')

    def __str__(self):
        return self.name


def check_for_assign(sender, instance, **kwargs):
    assign_if_check_passed(instance)


pre_save.connect(check_for_assign, sender=Activity)


def check_for_merge(sender, instance, **kwargs):
    merge_neighbour_activities(instance)


post_save.connect(check_for_merge, sender=Activity)


def set_username(sender, instance, **kwargs):
    email = instance.email
    username = email[:30]
    n = 1
    while User.objects.exclude(pk=instance.pk).filter(username=username).exists():
        n += 1
        username = email[:(29 - len(str(n)))] + '-' + str(n)
    instance.username = username


pre_save.connect(set_username, sender=User)


def add_default_soldier_info(sender, instance, created, **kwargs):
    if created:
        # in case of first soldier from a specific subdivison use constant defaults,
        # otherwise use other soldier's fields
        if Soldier.objects.filter(subdivision=instance.subdivision).count() == 1:
            # use constant defaults
            for default_info in DEFAULT_SOLDIER_INFO:
                SoldierInfo.objects.create(name=default_info, soldier=instance)
        else:
            # select one soldier from the same subdivision
            same_subdivision_soldiers = Soldier.objects.filter(subdivision=instance.subdivision).exclude(pk=instance.pk)
            soldier_info_fields = SoldierInfo.objects.filter(soldier=same_subdivision_soldiers.first())
            for info in soldier_info_fields:
                SoldierInfo.objects.create(name=info.name, soldier=instance)


post_save.connect(add_default_soldier_info, sender=Soldier)
