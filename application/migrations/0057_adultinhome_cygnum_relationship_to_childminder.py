# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-02-27 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0056_merge_20190215_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='cygnum_relationship_to_childminder',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]