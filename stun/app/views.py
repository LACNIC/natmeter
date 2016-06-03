from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def home(request):
    return render(request, "home.html")


def script(request):
    return render(request, "script.html")


@csrf_exempt
def post(request):
    def parse_int(string, default=0):
        try:
            return int(string)
        except ValueError as e:
            print e
            return default

    if request.method != 'POST':
        return HttpResponse("Invalid method: %s" % request.method, content_type="text", status=400)

    import ast
    from libraries.classes import datetime_uy
    from models import StunIpAddress, StunMeasurement

    date = datetime_uy()

    data = ast.literal_eval(request.POST.get("data"))
    experiment_id = request.POST.get("experiment_id")
    tester_version = request.POST.get("tester_version")

    stun_measurement = StunMeasurement(
        client_test_date=date,
        server_test_date=date,
        experiment_id=experiment_id,
        tester_version=tester_version
    )
    stun_measurement.save()

    for ip_address in data:
        a = StunIpAddress(
            ip_address=ip_address,
            stun_measurement=stun_measurement
        )
        a.save()

    v4 = [a for a in data if ":" not in a]
    v6 = [a for a in data if ":" in a]
    print "STUN measurement saved. %.0f v4 addresses, %.0f v6 addresses" % (len(v4), len(v6))


    response = HttpResponse("OK", content_type="text")
    response['Access-Control-Allow-Origin'] = "*"
    return response