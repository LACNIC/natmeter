from django.conf.urls import url, patterns
from . import views
from django.conf.urls.static import static
import stun.settings as settings


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'charts/', views.charts, name='charts'),
    url(r'post/', views.post, name='post'),
    url(r'script/', views.script, name='script')

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
