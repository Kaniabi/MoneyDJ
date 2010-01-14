from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.money.views',
    (r'^(?:dashboard/)?$', 'dashboard.index'),
    (r'^accounts/(\d+)/$', 'accounts.view'),
    (r'^accounts/add/$', 'accounts.add')
    #(r'^transactions/$', 'transactions'),
)