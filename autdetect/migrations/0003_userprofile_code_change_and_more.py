# Generated by Django 5.0.6 on 2024-09-04 01:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autdetect', '0002_alter_psychologists_dni_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='code_change',
            field=models.CharField(blank=True, default=0, max_length=6),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 4, 2, 3, 37, 91216, tzinfo=datetime.timezone.utc)),
        ),
    ]
