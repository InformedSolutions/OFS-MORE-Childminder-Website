# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-26 11:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_auto_20180124_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='adult',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='childinhome',
            name='child',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
