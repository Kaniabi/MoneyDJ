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

    if (request.method == 'POST'):
        transaction_form = QuickTransactionForm(request.POST)
        if (transaction_form.is_valid()):
            transaction = transaction_form.save()
            transaction_form = QuickTransactionForm()
    else:
        transaction_form = QuickTransactionForm()

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
            return redirect(reverse('moneydj.accounts.views.view', args=[acc.id]))
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
    transaction = get_object_or_404(Transaction, pk=transaction, user=request.user)

    if (request.method == "POST"):


    return render_to_response('account_edit.html', { 'form': form }, context_instance=RequestContext(request))
