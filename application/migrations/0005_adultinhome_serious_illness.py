# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-11 11:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_remove_healthcheckserious_serious_illness'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='serious_illness',
            field=models.BooleanField(default=False),
        ),
    ]
