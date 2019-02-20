from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datadog import statsd
import stun.settings as settings
from app.models import StunMeasurement
from collections import Counter
import operator
from django.db.models import Q
from django.views.decorators.http import require_http_methods


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


def generic_reports(request, *args, **kwargs):
    dates = [
        sm.server_test_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) for sm in StunMeasurement.objects.get_results().filter(Q(**kwargs)).order_by('-server_test_date')
    ]

    lines = sorted_counter(Counter(dates))

    return HttpResponse(lines, content_type="text")


@csrf_exempt
@require_http_methods(["POST"])
def post(request):

    import ast, json
    from app.libraries.classes import datetime_uy
    from app.models import StunIpAddress, StunMeasurement, StunIpAddressChangeEvent
    from datetime import datetime

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
    ip_address_change_event = ast.literal_eval(post.get("ip_address_change_event"))
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


    stun_measurement = StunMeasurement(
        client_test_date=server_date,  # TODO fix this
        server_test_date=server_date,
        experiment_id=experiment_id,
        cookie=cookie,
        tester_version=tester_version,
        href=href,
        user_agent=user_agent
    )
    stun_measurement.save()

    statsd.increment(
        'Result via HTTP POST',
        tags=['type:HTTP', 'tester:NATMeter'] + settings.DATADOG_DEFAULT_TAGS
    )

    for ip_address in addresses["public"]:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement,
            ip_address_kind=StunIpAddress.Kinds.REMOTE
        )
        stun_measurement.stunipaddress_set.add(a)

    for ip_address in addresses["private"]:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement,
            ip_address_kind=StunIpAddress.Kinds.LOCAL
        )
        stun_measurement.stunipaddress_set.add(a)

    current_ = ip_address_change_event["current"]
    previous_ = ip_address_change_event["previous"]
    if current_ is not "" and previous_ is not "":
        change = StunIpAddressChangeEvent(
            previous=previous_,
            current=current_,
            stun_measurement=stun_measurement
        )
        stun_measurement.stunipaddresschangeevent_set.add(change)

    print "STUN measurement saved. %s" % (stun_measurement)

    response = HttpResponse("OK", content_type="text")
    response['Access-Control-Allow-Origin'] = "*"
    return response
