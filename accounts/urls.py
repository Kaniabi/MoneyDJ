from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.accounts.views',
    (r'^$', 'index'),
    (r'^(\d+)/$', 'view'),
    (r'^add/$', 'add'),
    (r'^(\d+)/transaction/(\d+)$', 'view_transaction'),
    (r'^(\d+)/transaction/add/$', 'add_transaction'),
)
