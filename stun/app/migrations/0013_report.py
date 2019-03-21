# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_announcingasn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('v6_avg', models.FloatField()),
                ('v4_avg', models.FloatField()),
                ('v6_max', models.FloatField()),
                ('v4_max', models.FloatField()),
                ('all_nat', models.FloatField()),
                ('all_nat_world', models.FloatField()),
                ('v4_nat', models.FloatField()),
                ('v4_nat_world', models.FloatField()),
                ('v6_nat', models.FloatField()),
                ('v6_nat_world', models.FloatField()),
                ('v6_only', models.FloatField()),
                ('v6_with_v4_capacity', models.FloatField()),
                ('v6_with_v4_capacity_world', models.FloatField()),
                ('dualstack', models.FloatField()),
                ('dualstack_world', models.FloatField()),
                ('npt', models.FloatField()),
                ('npt_world', models.FloatField()),
                ('public_pfxs_nat_free_0_false_percentage', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
