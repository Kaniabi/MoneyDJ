from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^register/$', 'moneydj.moneyuser.views.register'),
    (r'^$', 'moneydj.moneyuser.views.profile')
    #(r'^transactions/$', 'transactions'),
)