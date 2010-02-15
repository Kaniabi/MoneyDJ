from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.tags.views',
    (r'^suggest/$', 'get_tag_suggestions')
)