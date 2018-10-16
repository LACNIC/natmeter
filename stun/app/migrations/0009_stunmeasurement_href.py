# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_stunmeasurement_noisy_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='href',
            field=models.CharField(default=None, max_length=1024, null=True, help_text='Site providing the results'),
            preserve_default=True,
        ),
    ]
