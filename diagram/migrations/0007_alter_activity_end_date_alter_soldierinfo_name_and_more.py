# Generated by Django 4.1.4 on 2023-01-15 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diagram', '0006_remove_soldier_driving_license_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='end_date',
            field=models.DateField(blank=True, verbose_name='data zakończenia'),
        ),
        migrations.AlterField(
            model_name='soldierinfo',
            name='name',
            field=models.CharField(max_length=20, verbose_name='nazwa'),
        ),
        migrations.CreateModel(
            name='EverydayActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('SŁ.OF', 'służba oficera'), ('SŁ.POM', 'służba pomocnika'), ('SŁ.PDF', 'służba podoficera'), ('SŁ.DYŻ', 'służba dyżurnego'), ('SŁ.PST', 'służba PST'), ('SŁ.PKT', 'służba PKT'), ('PA GAR', 'służba PA garnizonu'), ('PA JW', 'służba PA JW'), ('OKO', 'OKO')], max_length=30, verbose_name='nazwa')),
                ('how_many', models.IntegerField(default=1, verbose_name='ile dziennie')),
                ('subdivision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='diagram.subdivision', verbose_name='pododdział')),
            ],
        ),
    ]
