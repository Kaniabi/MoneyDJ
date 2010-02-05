from decimal import *
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from moneydj.accounts.forms import *
from moneydj.money.models import *

@login_required
def index(request):
    try:
        accounts = Account.objects.filter(user=request.user)
    except Account.DoesNotExist:
        raise Http404

    return render_to_response("account_index.html", { "accounts": accounts }, context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def view(request, id):
    """Lists the transactions in an account"""
    acc = get_object_or_404(Account, pk=id, user=request.user)

    if request.method == 'POST':
        transaction_form = QuickTransactionForm(request.POST)
        if 'account' not in request.POST.keys() or request.POST['account'] != id:
            raise Http404
        
        if (transaction_form.is_valid()):
            transaction = transaction_form.save()
            acc.update_balance()
            transaction_form = QuickTransactionForm(initial={ 'account': acc.pk, 'user': request.user.pk })
    else:
        transaction_form = QuickTransactionForm(initial={ 'account': acc.pk, 'user': request.user.pk })

    # Get all the transactions
    transactions = Transaction.objects.select_related().filter(account=acc).order_by('-date', '-date_created')

    return render_to_response('account_view.html', {
        'account': acc,
        'transactions': transactions,
        'transaction_form': transaction_form
    }, context_instance=RequestContext(request))

@login_required
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
            return redirect(reverse('moneydj.accounts.views.view', args=[acc.pk]))
    else:
        form = AccountForm()
    return render_to_response('account_add.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def add_transaction(request, account):
    """Adds a transaction to the specified account"""
    pass

@login_required
def edit_transaction(request, account, transaction):
    account = get_object_or_404(Account, pk=account, user=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction, account=account)
    
    if request.method == "POST":
        form = QuickTransactionForm(request.POST)
        if int(request.POST['account']) != account.pk:
            raise Http404
        
        if form.is_valid():
            form.save(instance=transaction)
            return redirect(reverse('moneydj.accounts.views.view', args=[transaction.account.pk]))
    else:
        tags = u''
        # Build the tag field
        for tl in transaction.taglink_set.all():
            tags = tags + tl.tag.name
            if tl.split != transaction.amount:
                tags = tags + u':' + tl.split
            tags = tags + u' '
            
        tags = tags.strip()
        data = {
            'date': transaction.date,
            'payee': transaction.payee.name,
            'amount': transaction.amount,
            'credit': transaction.credit,
            'transfer': transaction.transfer,
            'tags': tags,
            'account': account.pk
        }
        form = QuickTransactionForm(initial=data)

    return render_to_response('transaction_edit.html', { 'form': form, 'account': account, 'transaction': transaction }, context_instance=RequestContext(request))

@login_required
def delete_transaction(request, account, transaction):
    transaction = get_object_or_404(Transaction, pk=transaction, account=account, account__user=request.user)
    
    transaction.delete()
    transaction.account.update_balance(True)
    return redirect(reverse('moneydj.accounts.views.view', args=[account]))