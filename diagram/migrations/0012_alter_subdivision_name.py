# Generated by Django 4.1.4 on 2023-02-16 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagram', '0011_alter_subdivision_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subdivision',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='nazwa'),
        ),
    ]
