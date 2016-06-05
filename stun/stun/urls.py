from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urls = patterns('',
                    # Common urls
                       url(r'', include('app.urls'))
                       # url(r'admin/', include(admin.site.urls)),
                       )

# urls = patterns('',
#
#                 # API urls
#                 url(r'api/', include('simon_app.urls_api')),
#
#                 # Common urls
#                 url(r'', include('simon_app.urls'))
# )

# The /simon tree root in Apache
urlpatterns = patterns('',
                       url(r'', include(urls)),

                       # Uncomment the next line to enable the admin:
                       url(r'admin/', include(admin.site.urls)),
)
