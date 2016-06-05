from django.conf.urls import patterns, include, url
from django.contrib import admin

# urlpatterns = [
#     url(r'^stun/', include('app.urls')),
#     url(r'^admin/', include(admin.site.urls)),
# ]


urlpatterns = patterns('',
                       url(r'', include('app.urls')),
                       url(r'admin/', include(admin.site.urls)),
                       )
admin.autodiscover()
