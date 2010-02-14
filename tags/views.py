from money.models import Tag
from django.http import HttpResponse, HttpResponseBadRequest
try:
    import json
except ImportError:
    import simplejson as json

def get_tag_suggestions(request, suggest):
    tags = Tag.objects.filter(name__icontains=suggest)
    
    response = []
    for t in tags:
        response.append(t.name)
    
    return HttpResponse(json.dumps(response), content_type='application/javascript; charset=utf-8')