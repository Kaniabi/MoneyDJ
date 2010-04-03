from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.sync.views',
    url(r'^accounts/$', 'get_accounts', name='sync-accounts'),
    url(r'^transactions/$', 'get_transactions', name='sync-transactions')
)