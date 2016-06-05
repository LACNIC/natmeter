from django.conf.urls import url, patterns

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'script/', views.script, name='script')
)
