# Create your views here.
from django.shortcuts import render_to_response
from moneydj.money.models import Transaction, TagLink, Account
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Sum

@login_required
def index(request):
    # Get the users accounts
    accounts = Account.objects.filter(user=request.user).order_by('name')

    acc_total = 0
    for a in accounts:
        acc_total += a.balance
    
    # Get the latest transactions
    latest_transactions = Transaction.objects.filter(account__user=request.user).order_by('-date')[:10]
    
    return render_to_response('dashboard.html', {'acc_total': acc_total, 'transactions': latest_transactions, 'accounts': accounts}, context_instance=RequestContext(request))
