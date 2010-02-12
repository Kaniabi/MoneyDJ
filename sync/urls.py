from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.sync.views',
    (r'^accounts/$', 'get_accounts'),
    (r'^transactions/$', 'get_transactions')
)