# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-02-04 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0050_application_reasons_known_to_social_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='reasons_known_to_social_services_pith',
            field=models.TextField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='reasons_known_to_social_services',
            field=models.TextField(default='', null=True),
        ),
    ]
