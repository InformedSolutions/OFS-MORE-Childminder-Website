# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-18 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0060_previousname_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_in_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_in_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_in_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_out_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_out_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantpersonaldetails',
            name='moved_out_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_in_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_in_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_in_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_out_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_out_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='moved_out_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousaddress',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
