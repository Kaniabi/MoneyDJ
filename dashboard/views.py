# Create your views here.
from django.shortcuts import render_to_response
from money.models import Transaction, TagLink, Account
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Sum

@login_required
def index(request):
    # Get the users accounts
    accounts = Account.objects.filter(user=request.user).order_by('name')
    
    # Get the latest transactions
    latest_transactions = Transaction.objects.filter(account__user=request.user).order_by('-date')[:10]
    
    # Get the tags for a tag cloud
    tags = TagLink.objects.filter(transaction__account__user=request.user, transaction__amount__gt=0, transaction__transfer=False).values('tag__name').annotate(total=Sum('split')).order_by('tag__name')[:20]
    
    return render_to_response('dashboard.html', {'transactions': latest_transactions, 'tags': tags, 'accounts': accounts}, context_instance=RequestContext(request))