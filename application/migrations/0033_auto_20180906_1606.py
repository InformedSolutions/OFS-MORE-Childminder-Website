# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-06 15:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0032_merge_20180903_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='capita',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='lived_abroad',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='military_base',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='on_update',
            field=models.NullBooleanField(),
        ),
    ]
