# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-27 13:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0020_nannyapplication_references_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arccomments',
            name='comment',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]