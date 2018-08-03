# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_stunipaddress_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='nat_free_0',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='nat_free_4',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='nat_free_6',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
    ]
