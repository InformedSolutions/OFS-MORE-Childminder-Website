# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-10-18 16:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0044_remove_application_publish_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='publish_details',
            field=models.NullBooleanField(default=None),
        ),
    ]
