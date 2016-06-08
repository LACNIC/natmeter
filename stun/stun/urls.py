from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urls = patterns('',
                # Common urls
                url(r'', include('app.urls'))
                )

# The /stun tree root in Apache
urlpatterns = patterns('',
                       url(r'', include(urls)),
                       # Uncomment the next line to enable the admin:
                       url(r'admin/', include(admin.site.urls)),
                       )
