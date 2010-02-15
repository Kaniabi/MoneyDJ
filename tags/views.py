from money.models import Tag
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import json
except ImportError:
    import simplejson as json

def get_tag_suggestions(request):
    if not request.GET['q']:
        return HttpResponseBadRequest()
    
    tags = Tag.objects.filter(name__icontains=request.GET['q']).order_by('name')
    
    response = []
    for t in tags:
        response.append(t.name)
    
    return HttpResponse(json.dumps(response), content_type='application/javascript; charset=utf-8')