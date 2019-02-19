from django.contrib import admin
from models import *


class StunGenericAdmin(admin.ModelAdmin):
    """
        Generic admin covering admin-wide
    """

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class StunMeasurementAdmin(StunGenericAdmin):

    list_display = ['server_test_date', 'href', 'nat_free_0', 'v6_count', 'v4_count', 'get_country', 'get_asn', 'already_processed']
    ordering = ['-server_test_date']
    search_fields = ['cookie']

    def resolve_announcing_asns(modeladmin, request, queryset):
        for q in queryset:
            ips = StunIpAddress.objects.filter(stun_measurement=q)
            for ip in ips:
                ip.resolve_announcing_asns()
    resolve_announcing_asns.short_description = "Resolve announcing ASNs for this IP address"

    actions = [resolve_announcing_asns]
    list_per_page = 1000


class StunIpAddressAdmin(StunGenericAdmin):
    list_display = ['ip_address', 'stun_measurement__cookie', 'stun_measurement']

    def stun_measurement__cookie(self, obj):
        return obj.stun_measurement.cookie

    stun_measurement__cookie.short_description = "Cookie stored in the client's browser"

    def resolve_announcing_asns(modeladmin, request, queryset):
        for q in queryset:
            q.resolve_announcing_asns()
    resolve_announcing_asns.short_description = "Resolve announcing ASNs for this IP address"

    actions = [resolve_announcing_asns]


class StunIpAddressChangeEventAdmin(StunGenericAdmin):
    list_display = ['previous', 'current', 'stun_measurement__server_test_date']

    def stun_measurement__server_test_date(self, obj):
        return obj.stun_measurement.server_test_date

    stun_measurement__server_test_date.short_description = "Date"

class AnnouncingAsnAdmin(StunGenericAdmin):
    pass

admin.site.register(StunMeasurement, StunMeasurementAdmin)
admin.site.register(StunIpAddress, StunIpAddressAdmin)
admin.site.register(StunIpAddressChangeEvent, StunIpAddressChangeEventAdmin)
admin.site.register(AnnouncingAsn, AnnouncingAsnAdmin)
