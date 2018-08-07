# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_stunmeasurement_npt'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='v4_count',
            field=models.IntegerField(default=0, help_text='IPv4 addresses count for that host', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='v6_count',
            field=models.IntegerField(default=0, help_text='IPv6 addresses count for that host', null=True),
            preserve_default=True,
        ),
    ]
