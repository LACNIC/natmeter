# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_report_window'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='v6_only_world',
            field=models.FloatField(default=-1),
            preserve_default=True,
        ),
    ]
