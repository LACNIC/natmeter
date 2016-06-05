from django.conf.urls import url, patterns

from . import views

# urlpatterns = [
#     url(r'^$', views.home, name='home'),
#     url(r'script/', views.script, name='script'),
#     url(r'post/', views.post, name='post')
# ]

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'script/', views.script, name='script')
)
