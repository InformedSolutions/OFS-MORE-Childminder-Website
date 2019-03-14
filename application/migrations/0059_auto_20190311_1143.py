# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-11 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0058_delete_applicationreference'),
    ]

    operations = [
        migrations.AddField(
            model_name='adultinhome',
            name='name_end_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='name_end_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='name_end_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='name_start_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='name_start_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adultinhome',
            name='name_start_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='end_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='end_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='end_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='start_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='start_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='applicantname',
            name='start_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='end_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='end_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='end_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='start_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='start_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='previousname',
            name='start_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
