# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-24 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0024_merge_20180816_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='eyfs',
            name='common_core_training',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='eyfs',
            name='eyfs_training',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='eyfs',
            name='no_training',
            field=models.NullBooleanField(default=None),
        ),
    ]
