# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20180806_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='npt',
            field=models.NullBooleanField(default=None, help_text='Usage of NPT'),
            preserve_default=True,
        ),
    ]
