from django.contrib import admin
from models import *


class StunGenericAdmin(admin.ModelAdmin):
    """
        Generic admin covering admin-wide
    """

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class StunMeasurementAdmin(StunGenericAdmin):

    list_display = ['server_test_date', 'href', 'nat_free_0', 'v6_count', 'v4_count', 'get_country']
    ordering = ['-server_test_date']
    search_fields = ['cookie']


class StunIpAddressAdmin(StunGenericAdmin):
    list_display = ['ip_address', 'stun_measurement__cookie']

    def stun_measurement__cookie(self, obj):
        return obj.stun_measurement.cookie

    stun_measurement__cookie.short_description = "Cookie stored in the client's browser"


class StunIpAddressChangeEventAdmin(StunGenericAdmin):
    list_display = ['previous', 'current', 'stun_measurement__server_test_date']

    def stun_measurement__server_test_date(self, obj):
        return obj.stun_measurement.server_test_date

    stun_measurement__server_test_date.short_description = "Date"


admin.site.register(StunMeasurement, StunMeasurementAdmin)
admin.site.register(StunIpAddress, StunIpAddressAdmin)
admin.site.register(StunIpAddressChangeEvent, StunIpAddressChangeEventAdmin)
