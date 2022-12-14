from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save

from diagram.text_choices import ranks, activity_names


class User(AbstractUser):
    subdivision = models.ForeignKey('Subdivision', on_delete=models.SET_NULL, null=True)


class Subdivision(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Soldier(models.Model):
    rank = models.CharField(max_length=20, choices=ranks)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.rank} {self.first_name} {self.last_name} ({self.subdivision})'


class Activity(models.Model):
    soldier = models.ForeignKey(Soldier, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=30, choices=activity_names)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.name}, {self.description} ({self.soldier})'


def set_username(sender, instance, **kwargs):
    email = instance.email
    username = email[:30]
    n = 1
    while User.objects.exclude(pk=instance.pk).filter(username=username).exists():
        n += 1
        username = email[:(29 - len(str(n)))] + '-' + str(n)
    instance.username = username


pre_save.connect(set_username, sender=User)