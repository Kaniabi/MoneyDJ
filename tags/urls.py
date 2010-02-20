from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.tags.views',
    (r'^$', 'index'),
    (r'^(\w+)/$', 'view_tag'),
    (r'^suggest/$', 'get_tag_suggestions')
)