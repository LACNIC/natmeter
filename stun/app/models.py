from __future__ import unicode_literals

from django.db import models


class StunMeasurement(models.Model):
    """
        Stun measurement class. Stores the results provided
        by the JavaScript STUN/TURN software probe.
    """
    test_date = models.DateTimeField()

    number = models.BigIntegerField(default=0)
    protocol = models.TextField(default="")
    sequence = models.BigIntegerField(default=0)
    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    sequence2 = models.BigIntegerField(default=0)
    typ = models.TextField(default="")
    host = models.TextField()
    gen = models.TextField(default="")
    number2 = models.BigIntegerField(default=0)
