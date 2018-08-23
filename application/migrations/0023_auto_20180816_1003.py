# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-16 09:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0022_auto_20180731_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arc',
            name='childcare_address_review',
            field=models.CharField(blank=True, choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='arc',
            name='childcare_training_review',
            field=models.CharField(blank=True, choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='arc',
            name='insurance_cover_review',
            field=models.CharField(blank=True, choices=[('NOT_STARTED', 'NOT_STARTED'), ('FLAGGED', 'FLAGGED'), ('COMPLETED', 'COMPLETED')], default='NOT_STARTED', max_length=50, null=True),
        ),
    ]