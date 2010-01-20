from moneydj.accounts.forms import *
from moneydj.money.models import *
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def view(request, id):
    """Lists the transactions in an account"""
    acc = get_object_or_404(Account, pk=id, user=request.user)
    
    if (request.method == 'POST'):
        transaction_form = QuickTransactionForm(request.POST)
        if (transaction_form.is_valid()):
            tr = Transaction()
            # Try to find an existing payee with that name
            payee = Payee.objects.filter(name__iexact=transaction_form.cleaned_data['payee'])
            
            if (len(payee) == 1):
                payee = payee[0]
            else:
                # Create a new payee
                payee = Payee(name=transaction_form.cleaned_data['payee'])
                payee.save()
                
            tr.payee = payee
                
            tr.account = acc
            tr.amount = transaction_form.cleaned_data['amount']
            tr.transfer = transaction_form.cleaned_data['transfer']
            tr.credit = transaction_form.cleaned_data['credit']
            tr.date = transaction_form.cleaned_data['date']
            tr.save()
            transaction_form = QuickTransactionForm()
    else:
        transaction_form = QuickTransactionForm()
    
    # Get all the transactions
    transactions = Transaction.objects.filter(account=acc).order_by('-date', '-date_created').select_related()

    return render_to_response('account_view.html', {
        'account': acc, 
        'transactions': transactions, 
        'transaction_form': transaction_form
    }, context_instance = RequestContext(request))

def add(request):
    """Adds an account"""
    if (request.method == 'POST'):
        form = AccountForm(request.POST)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.user = request.user
            acc.balance_updated = datetime.datetime.today()
            acc.starting_balance = acc.balance
            acc.save()
            return redirect(reverse('moneydj.accounts.views.view', args=[acc.id]))
    else:
        form = AccountForm()
    return render_to_response('account_add.html', {'form': form}, context_instance = RequestContext(request))

def add_transaction(request, account):
    """Adds a transaction to the specified account"""
    pass

def view_transaction(request, account, transaction):
    """Views a transaction"""
    pass