# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-23 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alpaca', '0011_session_emails_are_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='description',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='session',
            name='description',
            field=models.TextField(max_length=500),
        ),
    ]
