# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-09-06 15:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0034_auto_20180906_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='working_in_other_childminder_home',
            field=models.NullBooleanField(default=None),
        ),
    ]
