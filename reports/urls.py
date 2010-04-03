from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('moneydj.reports.views',
    url(r'^$', 'index', name='reports-index')
)