# Generated by Django 5.0.6 on 2024-09-19 23:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autdetect', '0004_alter_questionnaire_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionnaire',
            name='sexo',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 19, 23, 16, 9, 802329, tzinfo=datetime.timezone.utc)),
        ),
    ]