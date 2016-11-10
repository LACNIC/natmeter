from django.core.management.base import BaseCommand
from app.models import StunMeasurement
from app.static_defs import NOISY_PREFIXES
import csv
import datetime
import pytz
from stun.settings import STATIC_ROOT

class Command(BaseCommand):
    def handle(self, *args, **options):
        comments = []
        comments.append(["# This is a TAB separated values file containing the results gathered by the NAT Meter experiment (https://natmeter.labs.lacnic.net)."])
        comments.append(["# Private prefixes have been excluded."])
        # comments.append(["# Local IP Addressess:  (List) Those IP addresses that the host is able to see locally"])
        comments.append(["# Remote IP Addressess: (List) Those IP prefixes that the host is *not* able to see locally but the remote STUN server can"])
        # comments.append(["# STUN Measurement ID:  The measurement ID corresponding with a certain user. This field is a cookie stored in the user's browser."])

        comments.append(["# The following prefixes have been excluded (LACNIC's own networks)"])
        comments.append(['# ' + ', '.join(NOISY_PREFIXES)])
        # comments.append(['# If you know any other bias email {agustin | alejandro | carlos} at lacnic dot net.'])

        now = datetime.datetime.now().replace(second=0, microsecond=0)
        uy = pytz.timezone('America/Montevideo')
        now = uy.localize(now)
        comments.append(["# Data exported at %s (%s)." % (now, now.tzinfo)])

        sms = StunMeasurement.objects.all().order_by('-server_test_date')
        with open(STATIC_ROOT + '/results.csv', 'wb') as csvfile:

            # fieldnames = ['local_ip_addresses', 'remote_ip_addresses', 'date']
            fieldnames = ['remote_ip_addresses', 'date']

            writer = csv.writer(csvfile, delimiter='\t')

            for c in comments:
                writer.writerow(c)

            writer.writerow([])

            writer.writerow(fieldnames)
            for sm in sms:
                local_addresses = StunMeasurement.objects.show_addresses_to_the_world(sm.get_local_addresses())
                stun_addresses = StunMeasurement.objects.show_addresses_to_the_world(sm.get_remote_addresses())

                if len(stun_addresses) == 0: continue

                date = sm.server_test_date.date()
                # writer.writerow([local_addresses] + [stun_addresses] + [date])
                writer.writerow([stun_addresses] + [date])
