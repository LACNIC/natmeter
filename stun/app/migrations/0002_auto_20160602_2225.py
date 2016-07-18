# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 22:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stunmeasurement',
            name='client_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 2, 22, 24, 59, 920358, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='server_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 2, 22, 24, 59, 920300, tzinfo=utc)),
        ),
    ]