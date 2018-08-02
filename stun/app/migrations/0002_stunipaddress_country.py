# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stunipaddress',
            name='country',
            field=models.CharField(default='DEF', help_text='Country after IP-->Country resolution', max_length=3),
            preserve_default=True,
        ),
    ]
