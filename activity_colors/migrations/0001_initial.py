# Generated by Django 4.1.4 on 2023-01-26 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('diagram', '0009_alter_everydayactivity_name_delete_activitycolor'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_name', models.CharField(max_length=30, verbose_name='aktywność')),
                ('color_hex', models.CharField(max_length=7, verbose_name='kolor')),
                ('subdivision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='diagram.subdivision', verbose_name='pododdział')),
            ],
        ),
    ]