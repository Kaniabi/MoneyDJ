from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('moneydj.tags.views',
    url(r'^$', 'index', name='tag-index'),
    url(r'^suggest/$', 'get_tag_suggestions', name='tag-suggestions'),
    url(r'^suggest/(\d+)/$', 'get_tag_suggestions_for_payee', name='tag-payee-suggestions'),
    url(r'^view/([A-Za-z0-9_&-]+)/$', 'view_tag', name='tag-view')
)
