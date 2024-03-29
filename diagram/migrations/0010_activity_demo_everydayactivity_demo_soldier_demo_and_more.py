# Generated by Django 4.1.4 on 2023-02-14 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagram', '0009_alter_everydayactivity_name_delete_activitycolor'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='demo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='everydayactivity',
            name='demo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='soldier',
            name='demo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='soldierinfo',
            name='demo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subdivision',
            name='demo',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(choices=[('', ''), ('DYŻUR', 'dyżur'), ('HDK', 'HDK'), ('INNE', 'inne'), ('KURS', 'kurs'), ('L4', 'L4 - zwolnienie lekarskie'), ('OKO', 'OKO'), ('PO SŁ.', 'po służbie'), ('PA GAR', 'pododdział alarmowy garnizonu'), ('PA JW', 'pododdział alarmowy JW'), ('PS', 'podróż służbowa'), ('POLIG', 'poligon'), ('SŁ.DYŻ', 'służba dyżurnego'), ('SŁ.OF', 'służba oficera'), ('SŁ.PKT', 'służba PKT'), ('SŁ.PDF', 'służba podoficera'), ('SŁ.POM', 'służba pomocnika'), ('SŁ.PST', 'służba PST'), ('UR.DOD', 'urlop dodatkowy'), ('UR.OJC', 'urlop ojcowski'), ('UR.OK', 'urlop okolicznościowy'), ('UR.SZK', 'urlop szkoleniowy'), ('UR.WYC', 'urlop wychowawczy'), ('UR.WYP', 'urlop wypoczynkowy'), ('WOLNE', 'wolne')], max_length=30, verbose_name='nazwa'),
        ),
        migrations.AlterField(
            model_name='everydayactivity',
            name='name',
            field=models.CharField(choices=[('SŁ.OF', 'służba oficera'), ('SŁ.POM', 'służba pomocnika'), ('SŁ.PDF', 'służba podoficera'), ('SŁ.DYŻ', 'służba dyżurnego'), ('SŁ.PST', 'służba PST'), ('SŁ.PKT', 'służba PKT'), ('PA GAR', 'pododdział alarmowy garnizonu'), ('PA JW', 'pododdział alarmowy JW'), ('OKO', 'OKO')], max_length=30, verbose_name='nazwa'),
        ),
    ]
