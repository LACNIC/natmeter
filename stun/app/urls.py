from django.conf.urls import url, patterns
from . import views
from django.conf.urls.static import static
import stun.settings as settings

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'charts/', views.charts, name='charts'),
    url(r'post/', views.post, name='post'),
    url(r'reports/report_nat_free_0_true', views.generic_reports, {'nat_free_0': True}, name='report_nat_free_0_true'),
    url(r'reports/report_nat_free_0_false', views.generic_reports, {'nat_free_0': False}, name='report_nat_free_0_false'),
    url(r'reports/report_nat_free_4_true', views.generic_reports, {'nat_free_4': True}, name='report_nat_free_4_true'),
    url(r'reports/report_nat_free_4_false', views.generic_reports, {'nat_free_4': False}, name='report_nat_free_4_false'),
    url(r'reports/report_nat_free_6_true', views.generic_reports, {'nat_free_6': True}, name='report_nat_free_6_true'),
    url(r'reports/report_nat_free_6_false', views.generic_reports, {'nat_free_6': False}, name='report_nat_free_6_false'),
    url(r'script/', views.script, name='script')

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
