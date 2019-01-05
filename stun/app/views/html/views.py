from app.caching.caching import cache as cache
from collections import defaultdict
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from app.models import StunMeasurement, StunMeasurementManager
import json
import requests
import operator
import stun.settings as settings


# Aux
def rec_dd():
    return defaultdict(rec_dd)


def base_render(request, template):
    return render(request, template, {'debug': settings.DEBUG})


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

    v6_avg_cached = cache.get(cache.keys.v6_avg)['v6_count__avg']
    v4_avg_cached = cache.get(cache.keys.v4_avg)['v4_count__avg']

    nat = rec_dd()
    nat['all']['lac'] = cache.get(cache.keys.all_nat, 0)
    nat['all']['world'] = cache.get(cache.keys.all_nat_world, 0)

    nat['v4']['lac'] = cache.get(cache.keys.v4_nat, 0)
    nat['v4']['world'] = cache.get(cache.keys.v4_nat_world, 0)

    nat['v6']['lac'] = cache.get(cache.keys.v6_nat, 0)
    nat['v6']['world'] = cache.get(cache.keys.v6_nat_world, 0)

    v6_with_v4_cap = rec_dd()
    v6_with_v4_cap['lac'] = cache.get(cache.keys.v6_with_v4_capacity)
    v6_with_v4_cap['world'] = cache.get(cache.keys.v6_with_v4_capacity_world)

    dualstack = rec_dd()
    dualstack['lac'] = cache.get(cache.keys.dualstack)
    dualstack['world'] = cache.get(cache.keys.dualstack_world)

    v6_only = cache.get(cache.keys.v6_only)

    npt = rec_dd()
    npt['lac'] = cache.get(cache.keys.npt)
    npt['world'] = cache.get(cache.keys.npt_world)

    country_participation_counter_cached = cache.get(cache.keys.country_participation)

    public_pfxs_ratio = cache.get(cache.keys.public_pfxs_nat_free_0_false_percentage)

    private_prefix_counter_cached = cache.get(cache.keys.private_prefixes)

    # Country participation chart
    total = sum(country_participation_counter_cached.values())
    most_common = country_participation_counter_cached.most_common(n=3)
    country_participation_top = [(p[0], 1.0 * p[1]) for p in most_common]
    country_participation_top.append(
        ("Others", 1.0 * (total - sum(p[1] for p in most_common)))
    )  # Others
    country_participation_top = sorted(dict(country_participation_top).items(), key=operator.itemgetter(1))

    lim = 10
    private_prefix_counter_cached_top = [
        ("%02d) %s" % (i + 1, ppc[0]), ppc[1]) for i, ppc in
        enumerate(sorted(private_prefix_counter_cached, key=operator.itemgetter(1), reverse=True)[:lim])
    ]

    data = dict(
        x=json.dumps(
            [p[0] for p in private_prefix_counter_cached_top]
        ),
        y=json.dumps(
            [p[1] for p in private_prefix_counter_cached_top]
        ),
        divId="prefix_counter",
        labels=json.dumps(["Cantidad de mediciones por prefijo"]),
        kind='BarChart',
        colors=json.dumps(['#C53425']),
        xType='string'
    )
    private_prefix_chart = requests.post(settings.CHARTS_URL + "/code/", data=data).text

    ctx = RequestContext(
        request,
        {
            "v6_avg": v6_avg_cached,
            "v4_avg": v4_avg_cached,
            "nat": nat,
            "npt": npt,

            "v6_with_v4_cap": v6_with_v4_cap,
            "dualstack": dualstack,
            "v6_only": v6_only,

            "public_pfxs_ratio": public_pfxs_ratio,

            "country_participation": country_participation_top,
            "private_prefix_chart": private_prefix_chart
        }
    )

    return render_to_response("charts.html", ctx)
