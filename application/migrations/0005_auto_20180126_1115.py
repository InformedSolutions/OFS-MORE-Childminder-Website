# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-26 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20180126_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='adults_in_home',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='application',
            name='children_in_home',
            field=models.NullBooleanField(),
        ),
    ]