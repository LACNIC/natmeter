# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20190324_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='n_addr_dotlocal',
            field=models.IntegerField(default=-1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='n_addr_local',
            field=models.IntegerField(default=-1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='n_addr_remote',
            field=models.IntegerField(default=-1),
            preserve_default=True,
        ),
    ]
