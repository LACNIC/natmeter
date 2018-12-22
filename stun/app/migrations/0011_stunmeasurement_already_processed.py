# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_stunmeasurement_user_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='already_processed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
