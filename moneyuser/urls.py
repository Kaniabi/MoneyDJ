from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^$', 'moneydj.moneyuser.views.profile')
    #(r'^transactions/$', 'transactions'),
)