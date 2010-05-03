from django.conf.urls.defaults import *
from moneydj.moneyuser.forms import LoginForm

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'authentication_form': LoginForm}, name='user-login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='user-logout'),
    url(r'^register/$', 'moneydj.moneyuser.views.register', name='user-register'),
    url(r'^$', 'moneydj.moneyuser.views.profile', name='user-profile')
    #(r'^transactions/$', 'transactions'),
)
