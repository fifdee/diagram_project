from django.db import models

from diagram.text_choices import Ranks, ActivityNames


class Subdivision(models.Model):
    name = models.CharField(max_length=30)


class Soldier(models.Model):
    rank = models.CharField(max_length=20, choices=Ranks.choices)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True)


class Activity(models.Model):
    soldier = models.ForeignKey(Soldier, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=30, choices=ActivityNames)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
