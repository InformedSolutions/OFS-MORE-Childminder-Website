# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-29 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_auto_20180823_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='publish_details',
            field=models.NullBooleanField(default=None),
        ),
    ]
