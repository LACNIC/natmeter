from django.conf.urls import url, patterns, include
from . import views
from django.conf.urls.static import static
import stun.settings as settings

# living under /reports
reports = patterns(
    '',

    #  'ips__gt': 0
    url(r'nat_free_0_true', views.generic_reports, {'nat_free_0': True, 'ips__gt': 0}, name='report_nat_free_0_true'),
    url(r'nat_free_0_false', views.generic_reports, {'nat_free_0': False, 'ips__gt': 0}, name='report_nat_free_0_false'),
    url(r'nat_free_4_true', views.generic_reports, {'nat_free_4': True, 'ips__gt': 0}, name='report_nat_free_4_true'),
    url(r'nat_free_4_false', views.generic_reports, {'nat_free_4': False, 'ips__gt': 0}, name='report_nat_free_4_false'),
    url(r'nat_free_6_true', views.generic_reports, {'nat_free_6': True, 'v6_count__gt': 0, 'ips__gt': 0}, name='report_nat_free_6_true'),
    url(r'nat_free_6_false', views.generic_reports, {'nat_free_6': False, 'v6_count__gt': 0, 'ips__gt': 0}, name='report_nat_free_6_false'),
    url(r'dualstack_true', views.generic_reports, {'dualstack': True, 'ips__gt': 0}, name='report_dualstack_true'),
    url(r'dualstack_false', views.generic_reports, {'dualstack': False, 'ips__gt': 0}, name='report_dualstack_false'),
    url(r'npt_true', views.generic_reports, {'npt': True, 'ips__gt': 0}, name='report_npt_false'),
    url(r'npt_false', views.generic_reports, {'npt': False, 'ips__gt': 0}, name='report_npt_false'),
    url(r'v4_only', views.generic_reports, {'v6_count': 0, 'ips__gt': 0}, name='report_npt_false'),
    url(r'v6_only', views.generic_reports, {'v4_count': 0, 'ips__gt': 0}, name='report_npt_false'),

    url(r'dotlocal_ips__gt_0', views.dotlocal_reports, {'n_addr_dotlocal__gt': 0}, name='dotlocal_ips__gt_0'),
    url(r'all', views.dotlocal_reports, {}, name='all'),

    url(r'local_ips_0', views.generic_reports, {'n_addr_local': 0}, name='local_ips_0'),
    url(r'local_ips__gt_0', views.generic_reports, {'n_addr_local__gt': 0}, name='local_ips__gt_0'),
    url(r'remote_ips_0', views.generic_reports, {'n_addr_remote': 0}, name='remote_ips_0'),
    url(r'remote_ips__gt_0', views.generic_reports, {'n_addr_remote__gt': 0}, name='remote_ips__gt_0'),
    url(r'remote_local_0', views.generic_reports, {'n_addr_remote': 0, 'n_addr_local': 0}, name='remote_local_0'),


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

