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

    date = datetime_uy()

    data = ast.literal_eval(request.POST.get("data"))
    ip_address_change_event = ast.literal_eval(request.POST.get("ip_address_change_event"))
    experiment_id = request.POST.get("experiment_id")
    tester_version = request.POST.get("tester_version")
    cookie = request.POST.get("cookie")

    stun_measurement = StunMeasurement(
        client_test_date=date,  # TODO fix this
        server_test_date=date,
        experiment_id=experiment_id,
        cookie=cookie,
        tester_version=tester_version
    )
    stun_measurement.save()

    for ip_address in data:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement
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
