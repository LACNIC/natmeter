from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urls = patterns(
    '',
    # Common urls
    url(r'', include('app.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns = patterns(
    '',
    url(r'', include(urls)),
    url(r'admin/', include(admin.site.urls)),
)
