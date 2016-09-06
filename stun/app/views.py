from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def home(request):
    return render(request, "home.html")


def script(request):
    return render(request, "script.html")


@csrf_exempt
def post(request):
    if request.method != 'POST':
        return HttpResponse("Invalid method: %s" % request.method, content_type="text", status=400)

    import ast
    from libraries.classes import datetime_uy
    from models import StunIpAddress, StunMeasurement, StunIpAddressChangeEvent
    from datetime import datetime

    server_date = datetime_uy()
    client_date = request.POST.get("date")

    try:
        client_date = datetime.strptime(client_date.split(" GMT")[0], "%a %b %d %Y %H:%M:%S")
    except:  # broad..
        client_date = server_date

    experiment_id = request.POST.get("experiment_id")
    cookie = request.POST.get("cookie")
    addresses = ast.literal_eval(request.POST.get("addresses"))
    ip_address_change_event = ast.literal_eval(request.POST.get("ip_address_change_event"))
    tester_version = request.POST.get("tester_version")

    stun_measurement = StunMeasurement(
        client_test_date=server_date,  # TODO fix this
        server_test_date=server_date,
        experiment_id=experiment_id,
        cookie=cookie,
        tester_version=tester_version
    )
    stun_measurement.save()

    for ip_address in addresses["public"]:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement,
            ip_address_kind=StunIpAddress.Kinds.PUBLIC
        )
        stun_measurement.stunipaddress_set.add(a)

    for ip_address in addresses["private"]:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement,
            ip_address_kind=StunIpAddress.Kinds.PRIVATE
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
