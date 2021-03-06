from app.caching.caching import cache as cache
from collections import defaultdict
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from app.models import StunMeasurement, StunMeasurementManager, Report
import json
import requests
import operator
import stun.settings as settings


# Aux
def rec_dd():
    return defaultdict(rec_dd)


def base_render(request, template, ctx={}):
    ctx.update({'debug': settings.DEBUG})
    return render(request, template, ctx)


def home(request):
    return base_render(request, "home.html")


def script(request):
    return base_render(request, "script.html")


def cookies(request):
    return base_render(request, "cookies.html")


def charts(request):
    """
    :param request:
    :return:
    """

    first = Report.objects.order_by('-date')
    print first
    report = first.first()

    # country_participation = cache.get(cache.keys.country_participation)

    # public_pfxs_ratio = cache.get(cache.keys.public_pfxs_nat_free_0_false_percentage)

    # private_prefix_counter_cached = cache.get(cache.keys.private_prefixes)

    # Country participation chart
    country_participation = StunMeasurement.objects.get_country_participation()
    total = sum(country_participation.values())
    most_common = country_participation.most_common(n=5)
    country_participation_top = [(p[0], 1.0 * p[1]) for p in most_common]
    country_participation_top.append(
        ("Others", 1.0 * (total - sum(p[1] for p in most_common)))
    )  # Others
    country_participation_top = sorted(dict(country_participation_top).items(), key=operator.itemgetter(1))

    # lim = 10
    # private_prefix_counter_cached_top = [
    #     ("%02d) %s" % (i + 1, ppc[0]), ppc[1]) for i, ppc in
    #     enumerate(sorted(private_prefix_counter_cached, key=operator.itemgetter(1), reverse=True)[:lim])
    # ]
    #
    # data = dict(
    #     x=json.dumps(
    #         [p[0] for p in private_prefix_counter_cached_top]
    #     ),
    #     y=json.dumps(
    #         [p[1] for p in private_prefix_counter_cached_top]
    #     ),
    #     divId="prefix_counter",
    #     labels=json.dumps(["Cantidad de mediciones por prefijo"]),
    #     kind='BarChart',
    #     colors=json.dumps(['#C53425']),
    #     xType='string'
    # )
    # private_prefix_chart = requests.post(settings.CHARTS_URL + "/code/", data=data).text

    ctx = {
        "report": report,
        # "v4_avg": v4_avg_cached,
        # "nat": nat,
        # "npt": npt,
        #
        # "v6_with_v4_cap": v6_with_v4_cap,
        # "dualstack": dualstack,
        # "v6_only": v6_only,
        #
        # "public_pfxs_ratio": public_pfxs_ratio,
        #
        "country_participation": country_participation_top,
        # "private_prefix_chart": private_prefix_chart
    }

    return base_render(request, "charts.html", ctx=ctx)
    # return render_to_response("charts.html", ctx)
