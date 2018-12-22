from django.conf.urls import url, patterns, include
from . import views
from django.conf.urls.static import static
import stun.settings as settings

# living under /reports
reports = patterns(
    '',
    url(r'nat_free_0_true', views.generic_reports, {'nat_free_0': True}, name='report_nat_free_0_true'),
    url(r'nat_free_0_false', views.generic_reports, {'nat_free_0': False}, name='report_nat_free_0_false'),
    url(r'nat_free_4_true', views.generic_reports, {'nat_free_4': True}, name='report_nat_free_4_true'),
    url(r'nat_free_4_false', views.generic_reports, {'nat_free_4': False}, name='report_nat_free_4_false'),
    url(r'nat_free_6_true', views.generic_reports, {'nat_free_6': True, 'v6_count__gt': 0}, name='report_nat_free_6_true'),
    url(r'nat_free_6_false', views.generic_reports, {'nat_free_6': False, 'v6_count__gt': 0}, name='report_nat_free_6_false'),
    url(r'dualstack_true', views.generic_reports, {'dualstack': True}, name='report_dualstack_true'),
    url(r'dualstack_false', views.generic_reports, {'dualstack': False}, name='report_dualstack_false'),
    url(r'npt_true', views.generic_reports, {'npt': True}, name='report_npt_false'),
    url(r'npt_false', views.generic_reports, {'npt': False}, name='report_npt_false'),
    url(r'v4_only', views.generic_reports, {'v6_count': 0}, name='report_npt_false'),
    url(r'v6_only', views.generic_reports, {'v4_count': 0}, name='report_npt_false'),
)

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'charts/', views.charts, name='charts'),
    url(r'post/', views.post, name='post'),
    url(r'reports/', include(reports)),
    url(r'script/', views.script, name='script'),
    url(r'cookies/', views.cookies, name='cookies')

) + reports + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

