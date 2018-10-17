# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_stunmeasurement_href'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='user_agent',
            field=models.CharField(default=None, max_length=1024, null=True, help_text='User Agent'),
            preserve_default=True,
        ),
    ]
