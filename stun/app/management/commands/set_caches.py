from django.core.management.base import BaseCommand
from django.db import models
from app.caching.caching import cache
from app.models import StunMeasurement, Report
from statsd import StatsClient




class Command(BaseCommand):
    def handle(self, *args, **options):
        # old = cache.set

        # statsd = StatsClient()
        #
        # @statsd.timer('cache.set')
        # def new(k, v):
        #     print "Setting {key}".format(key=k)
        #     old(k, v)

        report = Report()
        report.set_values()
        report.save()



def get_announcements():
    import csv
    import requests
    import StringIO
    from collections import defaultdict

    CC = 1
    ALLOC = 2
    ADV = 7
    data = requests.get('http://labs.apnic.net/dists/v4.csv').text

    announcements = defaultdict(int)
    csvreader = csv.reader(StringIO.StringIO(data))
    for i in range(16):
        csvreader.next()
    for line in csvreader:
        #     line[CC], line[ALLOC], line[ADV]
        try:
            announcements[line[CC]] = line[ADV]
        except IndexError as e:
            continue
    return announcements
