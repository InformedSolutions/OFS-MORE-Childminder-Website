# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-11 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_adultinhome_hospital_admission'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='current_treatment',
            field=models.BooleanField(default=False),
        ),
    ]
