from django.conf.urls.defaults import patterns

urlpatterns = patterns('moneydj.tags.views',
    (r'^$', 'index'),
    (r'^suggest/$', 'get_tag_suggestions'),
    (r'^suggest/(\d+)/$', 'get_tag_suggestions_for_payee'),
    (r'^view/(\w+)/$', 'view_tag')
)