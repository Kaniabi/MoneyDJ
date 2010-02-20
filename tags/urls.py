from django.conf.urls.defaults import *

urlpatterns = patterns('moneydj.tags.views',
    (r'^$', 'index'),
    (r'^suggest/$', 'get_tag_suggestions'),
    (r'^view/(\w+)/$', 'view_tag')
)