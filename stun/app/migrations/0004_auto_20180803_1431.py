# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180803_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunmeasurement',
            name='dualstack',
            field=models.NullBooleanField(default=None, help_text='Dualstack detected'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='nat_free_0',
            field=models.NullBooleanField(default=None, help_text='Any kind of NAT'),
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='nat_free_4',
            field=models.NullBooleanField(default=None, help_text='NAT'),
        ),
    ]
