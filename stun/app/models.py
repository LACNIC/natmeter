from __future__ import unicode_literals
from libraries.classes import *
from django.db import models
from django.utils.timezone import now

class StunMeasurement(models.Model):
    """
        Stun measurement class. Stores the results provided
        by the JavaScript STUN/TURN software probe.
    """
    server_test_date = models.DateTimeField(default=now())
    client_test_date = models.DateTimeField(default=now())

    experiment_id = models.TextField(default="")
    tester_version = models.IntegerField(default=0)

    def is_behind_nat(self):
        return False

class StunIpAddress(models.Model):
    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)