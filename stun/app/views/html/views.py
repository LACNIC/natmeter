from app.caching.caching import cache as custom_cache
from collections import Counter
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import requires_csrf_token
from app.models import StunMeasurement, StunMeasurementManager
import json
import requests
import operator
import stun.settings as settings


def home(request):
    return render(request, "home.html")


def script(request):
    return render(request, "script.html")


def charts(request):
    """
    :param request:
    :return:
    """

    v6_avg_cached = custom_cache.get_or_set(custom_cache.keys.v6_avg, call=StunMeasurement.objects.v6_count_avg)
    v4_avg_cached = custom_cache.get_or_set(custom_cache.keys.v4_avg, call=StunMeasurement.objects.v4_count_avg)
    v6_max_cached = custom_cache.get_or_set(custom_cache.keys.v6_max, call=StunMeasurement.objects.v6_count_max)
    v4_max_cached = custom_cache.get_or_set(custom_cache.keys.v4_max, call=StunMeasurement.objects.v4_count_max)
    all_nat_cached = custom_cache.get_or_set(custom_cache.keys.all_nat, call=StunMeasurement.objects.nat_stats)
    v4_nat_cached = custom_cache.get_or_set(custom_cache.keys.v4_nat,
                                            call=StunMeasurement.objects.get_v4_nat_percentage)
    v6_nat_cached = custom_cache.get_or_set(custom_cache.keys.v6_nat,
                                            call=StunMeasurement.objects.get_v6_nat_percentage)
    v6_hosts_with_v4_capacity_cached = custom_cache.get_or_set(custom_cache.keys.v6_with_v4_capacity,
                                                               call=StunMeasurement.objects.get_v6_hosts_with_v4_capability_percentage)
    dualstack_cached = custom_cache.get_or_set(custom_cache.keys.dualstack,
                                               call=StunMeasurement.objects.get_dualstack_percentage)
    is_npt_cached = custom_cache.get_or_set(custom_cache.keys.npt, call=StunMeasurement.objects.get_npt_percentage)
    # nat_pressure_cached = custom_cache.get_or_set(custom_cache.keys.nat_pressure,
    #                                               call=StunMeasurement.objects.get_nat_time_pressure)
    country_participation_counter_cached = custom_cache.get_or_set(custom_cache.keys.country_participation,
                                                                   call=StunMeasurement.objects.get_country_participation)
    private_prefix_counter_cached = custom_cache.get_or_set(custom_cache.keys.private_prefixes,
                                                            call=StunMeasurement.objects.get_private_pfx_counter)

    # Country participation chart
    total = sum(country_participation_counter_cached.values())
    most_common = country_participation_counter_cached.most_common(n=3)
    country_participation_top = [(p[0], 1.0 * p[1]) for p in most_common]
    country_participation_top.append(
        ("Others", 1.0 * (total - sum(p[1] for p in most_common)))
    )  # Others
    country_participation_top = sorted(dict(country_participation_top).items(), key=operator.itemgetter(1))
    print(country_participation_top)

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
            "v6_max": v6_max_cached,
            "v4_max": v4_max_cached,
            "all_nat": all_nat_cached,
            "v4_nat": v4_nat_cached,
            "v6_nat": v6_nat_cached,
            "v6_with_v4_capacity": v6_hosts_with_v4_capacity_cached,
            "dualstack": dualstack_cached,
            "npt": is_npt_cached,
            # "hours": Counter(hours).most_common(n=1)[0][0],
            # "nat_pressure_chart": nat_pressure_chart,
            "country_participation": country_participation_top,
            "private_prefix_chart": private_prefix_chart
        }
    )

    return render_to_response("charts.html", ctx)
