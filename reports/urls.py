from django.conf.urls.defaults import patterns

urlpatterns = patterns('moneydj.reports.views',
    (r'^$', 'index')
)