import ast
import json
import operator
from collections import Counter
from datadog import statsd
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from app.libraries.classes import datetime_uy
from app.models import StunIpAddress, StunMeasurement
import stun.settings as settings


def sorted_counter(ctr):
    """
    :param ctr:
    :return: lines
    """
    counter = sorted(ctr.items(), key=operator.itemgetter(0))
    lines = []
    for date, count in counter:
        lines.append(
            "{y}-{m}-{d},{count}\n".format(y=date.year, m=date.month, d=date.day, count=count)
        )
    return lines


def reports(request, results):
    dates = [
        sm.server_test_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) for sm in results
    ]

    lines = sorted_counter(Counter(dates))

    return HttpResponse(lines, content_type="text")

def generic_reports(request, *args, **kwargs):
    return reports(
        request=request,
        results=StunMeasurement.objects.get_results().filter(Q(**kwargs)).order_by('-server_test_date')
    )


def dotlocal_reports(request, *args, **kwargs):
    return reports(
        request=request,
        results=StunMeasurement.objects.all().filter(Q(**kwargs)).order_by('-server_test_date')
    )


@csrf_exempt
@require_http_methods(["POST"])
def post(request):

    post = json.loads(request.body)

    server_date = datetime_uy()
    client_date = post.get("date")

    try:
        client_date = datetime.strptime(client_date.split(" GMT")[0], "%a %b %d %Y %H:%M:%S")
    except:  # broad..
        client_date = server_date
    finally:
        print client_date

    experiment_id = post.get("experiment_id")
    cookie = post.get("cookie")
    addresses = ast.literal_eval(post.get("addresses"))
    tester_version = post.get("tester_version")
    href = post.get("href")
    user_agent = post.get("user_agent")
    timers = post.get("timers")

    t0 = datetime.strptime(timers['init'][:-1], "%Y-%m-%dT%H:%M:%S.%f")
    for t, d in timers.items():
        t1 = datetime.strptime(d[:-1], "%Y-%m-%dT%H:%M:%S.%f")
        dt = t1 - t0

        statsd.timing(
            "timers.{timer}".format(timer=t),
            dt.total_seconds(),
            tags=['tester:NATMeter'] + settings.DATADOG_DEFAULT_TAGS
        )


    stun_measurement = StunMeasurement.objects.create(
        client_test_date=server_date,  # TODO fix this
        server_test_date=server_date,
        experiment_id=experiment_id,
        cookie=cookie,
        tester_version=tester_version,
        href=href,
        user_agent=user_agent
    )

    statsd.increment(
        'Result via HTTP POST',
        tags=['type:HTTP', 'tester:NATMeter'] + settings.DATADOG_DEFAULT_TAGS
    )

    for addresses, kind in zip([addresses["public"], addresses["private"]], [StunIpAddress.Kinds.REMOTE, StunIpAddress.Kinds.LOCAL]):
        for ip_address in addresses:

            if '.local' in ip_address:
                ip_address = StunIpAddress._meta.get_field_by_name('ip_address')[0].default
                kind = StunIpAddress.Kinds.DOTLOCAL

            a = StunIpAddress(
                ip_address=ip_address,
                stun_measurement=stun_measurement,
                ip_address_kind=kind
            )
            stun_measurement.stunipaddress_set.add(a)

    print "STUN measurement saved. %s" % (stun_measurement)

    response = HttpResponse("OK", content_type="text")
    response['Access-Control-Allow-Origin'] = "*"
    return response
