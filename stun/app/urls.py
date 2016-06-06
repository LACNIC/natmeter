from django.conf.urls import url, patterns
from . import views
from django.conf.urls.static import static
import settings as settings

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'script/', views.script, name='script')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
