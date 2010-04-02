from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.accounts.views',
    url(r'^$', 'index', name='account-index'),
    url(r'^(\d+)/$', 'view', name='account-view'),
    url(r'^(\d+)/edit/$', 'edit', name='account-edit'),
    url(r'^add/$', 'add', name='account-add'),
    url(r'^(\d+)/transaction/(\d+)/$', 'edit_transaction', name='transaction-edit'),
    url(r'^transaction/(\d+)/tag/$', 'tag_transaction', name='transaction-tag'),
    url(r'^(\d+)/transaction/(\d+)/delete/$', 'delete_transaction', name='transaction-delete'),
    url(r'^(\d+)/resync/$', 'resync', name='account-resync'),
    url(r'^payee/suggest/$', 'get_payee_suggestions', name='payee-suggestions')
)
