# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20180803_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='v4_only',
            field=models.NullBooleanField(default=None, help_text='v4 only host'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='v6_only',
            field=models.NullBooleanField(default=None, help_text='v6 only host'),
            preserve_default=True,
        ),
    ]
