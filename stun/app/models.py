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
    cookie = models.TextField(default="")
    tester_version = models.IntegerField(default=0)

    def is_behind_nat(self):
        return False

    def __str__(self):
        v4 = []
        v6 = []
        data = self.stunipaddress_set.all()
        for d in data:
            if ":" in d.ip_address:
                v4.append(d)
            else:
                v6.append(d)
        return "%.0f v4 addresses, %.0f v6 addresses" % (len(v4), len(v6))


class StunIpAddress(models.Model):
    """
        Place to store each IP address for that client for that measurement
    """
    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    stun_measurement = models.ForeignKey(StunMeasurement)