from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.dashboard.views',
    url(r'^$', 'index', name='dashboard')
)
