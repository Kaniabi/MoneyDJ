from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from money.models import Tag, Transaction, Payee
try:
    import json
except ImportError:
    from django.utils import simplejson as json
    
@login_required
def index(request):
    transactions = Transaction.objects.filter(taglink__id__isnull=True).order_by('-date')
    
    paginator = Paginator(transactions, 20)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        transactions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        transactions = paginator.page(paginator.num_pages)
        
    return render_to_response("tags_index.html", { "transactions": transactions }, context_instance=RequestContext(request))

@login_required
def view_tag(request, tag):
    # Get the right tag
    tag = get_object_or_404(Tag, name=tag)

    # Get the transactions related to the tag
    transactions = Transaction.objects.select_related().filter(taglink__tag=tag).order_by('-date')
    
    paginator = Paginator(transactions, 20)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        transactions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        transactions = paginator.page(paginator.num_pages)
    
    return render_to_response("tag_view.html", {'tag': tag, 'transactions': transactions }, context_instance=RequestContext(request))

def get_tag_suggestions(request):
    if 'q' not in request.GET or not request.GET['q']:
        return HttpResponseBadRequest()
    
    tags = Tag.objects.filter(name__icontains=request.GET['q'], transaction__account__user=request.user).order_by('name')
    
    response = [t.name for t in tags]
    
    return HttpResponse(json.dumps(response), content_type='application/javascript; charset=utf-8')

def get_tag_suggestions_for_payee(request, payee):
    payees = get_object_or_404(Payee, pk=payee).suggest_tags(request.user)
    
    return HttpResponse(json.dumps(payees), content_type='application/javascript; charset=utf-8')
