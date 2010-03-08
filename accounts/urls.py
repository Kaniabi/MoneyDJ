from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.accounts.views',
    (r'^$', 'index'),
    (r'^(\d+)/$', 'view'),
    (r'^(\d+)/edit/$', 'edit'),
    (r'^add/$', 'add'),
    (r'^(\d+)/transaction/(\d+)/$', 'edit_transaction'),
    (r'^(\d+)/transaction/add/$', 'add_transaction'),
    (r'^(\d+)/transaction/delete/(\d+)/$', 'delete_transaction'),
    (r'^(\d+)/resync/$', 'resync'),
    (r'^payee/suggest/$', 'get_payee_suggestions')
)
