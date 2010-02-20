from money.models import Tag, TagLink, Transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Sum
try:
    import json
except ImportError:
    import simplejson as json
    
@login_required
def index(request):
    tags = TagLink.objects.filter(transaction__account__user=request.user, transaction__credit=False, transaction__transfer=False).values('tag__name').annotate(total=Sum('split')).order_by('tag__name')[:20]
    return render_to_response("tags_index.html", { "tags": tags }, context_instance=RequestContext(request))

@login_required
def view_tag(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    transactions = Transaction.objects.filter(taglink__tag=tag).order_by('-date')
    return render_to_response("tag_view.html", {'tag': tag, 'transactions': transactions}, context_instance=RequestContext(request))

def get_tag_suggestions(request):
    if not request.GET['q']:
        return HttpResponseBadRequest()
    
    tags = Tag.objects.filter(name__icontains=request.GET['q']).order_by('name')
    
    response = []
    for t in tags:
        response.append(t.name)
    
    return HttpResponse(json.dumps(response), content_type='application/javascript; charset=utf-8')