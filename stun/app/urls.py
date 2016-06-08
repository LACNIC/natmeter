from django.conf.urls import url, patterns
from . import views
from django.conf.urls.static import static
import stun.settings as settings


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'script/', views.script, name='script'),
    url(r'post/', views.post, name='post')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
