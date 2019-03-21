# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_report_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='window',
            field=models.IntegerField(default=90, help_text='Time window this report covers (start=now-window)'),
            preserve_default=True,
        ),
    ]
