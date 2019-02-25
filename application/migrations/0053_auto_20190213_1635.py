# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-02-13 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0052_auto_20190207_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='previousname',
            name='first_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='previousname',
            name='last_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='previousname',
            name='middle_names',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='previousname',
            name='other_person_type',
            field=models.CharField(blank=True, choices=[('ADULT', 'ADULT'), ('CHILD', 'CHILD'), ('APPLICANT', 'APPLICANT')], max_length=200),
        ),
    ]