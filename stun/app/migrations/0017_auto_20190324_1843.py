# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_report_v6_only_world'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='nat64',
            field=models.FloatField(default=-1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='report',
            name='nat64_world',
            field=models.FloatField(default=-1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='nat64',
            field=models.NullBooleanField(default=None, help_text='Usage of NAT64'),
            preserve_default=True,
        ),
    ]
