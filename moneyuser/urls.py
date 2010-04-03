from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name='user-login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='user-logout'),
    url(r'^register/$', 'moneydj.moneyuser.views.register', name='user-register'),
    url(r'^$', 'moneydj.moneyuser.views.profile', name='user-profile')
    #(r'^transactions/$', 'transactions'),
)