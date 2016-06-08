# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20160602_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stunmeasurement',
            name='client_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 8, 17, 34, 1, 116248, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='server_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 8, 17, 34, 1, 116210, tzinfo=utc)),
        ),
    ]
