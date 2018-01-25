# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-24 17:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EYFS',
            fields=[
                ('eyfs_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('eyfs_understand', models.NullBooleanField()),
                ('eyfs_training_declare', models.NullBooleanField()),
                ('eyfs_questions_declare', models.NullBooleanField()),
                ('application_id', models.ForeignKey(db_column='application_id', on_delete=django.db.models.deletion.CASCADE, to='application.Application')),
            ],
            options={
                'db_table': 'EYFS',
            },
        ),
    ]