# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-07 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0035_auto_20180906_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='own_children',
            field=models.NullBooleanField(default=None),
        ),
    ]