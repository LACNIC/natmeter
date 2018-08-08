# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20180806_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='noisy_prefix',
            field=models.NullBooleanField(default=None, help_text='This measurement comes from one of the ignored prefixes (special cases)'),
            preserve_default=True,
        ),
    ]
