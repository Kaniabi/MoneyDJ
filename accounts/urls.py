from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.accounts.views',
    (r'^$', 'index'),
    (r'^(\d+)/$', 'view'),
    (r'^(\d+)/edit/$', 'edit'),
    (r'^add/$', 'add'),
    (r'^(\d+)/transaction/(\d+)/$', 'edit_transaction'),
    (r'^transaction/(\d+)/tag/$', 'tag_transaction'),
    (r'^(\d+)/transaction/(\d+)/delete/$', 'delete_transaction'),
    (r'^(\d+)/resync/$', 'resync'),
    (r'^payee/suggest/$', 'get_payee_suggestions')
)
