from django.contrib import admin
from models import *


class StunGenericAdmin(admin.ModelAdmin):
    """
        Generic admin covering admin-wide
    """

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


class StunMeasurementAdmin(StunGenericAdmin): pass


admin.site.register(StunMeasurement, StunMeasurementAdmin)
admin.site.register(StunIpAddress)
