# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-04 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0059_auto_20190903_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicantname',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
