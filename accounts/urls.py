from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.accounts.views',
    (r'^(\d+)/$', 'view'),
    (r'^add/$', 'add')
)
