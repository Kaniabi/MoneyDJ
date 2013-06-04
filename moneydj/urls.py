from django.conf.urls.defaults import *
from django.conf import settings

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
    (r'^$', 'moneydj.money.views.index'),
    (r'^user/', include('moneydj.moneyuser.urls')),
    (r'^dashboard/', include('moneydj.dashboard.urls')),
    (r'^accounts/', include('moneydj.accounts.urls')),
    (r'^sync/', include('moneydj.sync.urls')),
    (r'^tags/', include('moneydj.tags.urls')),
    (r'^reports/', include('moneydj.reports.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': 'django.conf'}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}), 
)
