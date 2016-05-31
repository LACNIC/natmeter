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
        return HttpResponse("Invalid method: %s" % request.method, content_type="text")

    data = request.POST.get("data").split()
    number = data[1]
    protocol = data[2]
    sequence = data[3]
    ip_address = data[4]
    sequence2 = data[5]
    typ = data[6]
    host = data[7]
    gen = data[8]
    number2 = data[9]

    response = HttpResponse("OK", content_type="text")
    response['Access-Control-Allow-Origin'] = "*"
    return response
