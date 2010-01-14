from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^moneydj/', include('moneydj.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^user/', include('moneydj.moneyuser.urls')),
    (r'^dashboard/', include('moneydj.dashboard.urls')),
    (r'^accounts/', include('moneydj.accounts.urls'))
)
