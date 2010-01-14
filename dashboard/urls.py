from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.dashboard.views',
    (r'^$', 'index')
)
