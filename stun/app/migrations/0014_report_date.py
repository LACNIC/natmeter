# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.libraries.classes


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='date',
            field=models.DateTimeField(default=app.libraries.classes.datetime_uy),
            preserve_default=True,
        ),
    ]
