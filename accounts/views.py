from accounts.forms import QuickTransactionForm, AccountForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from money.models import Account, Transaction, Payee, TagLink
import datetime
try:
    import json
except ImportError:
    from django.utils import simplejson as json

@login_required
def index(request):
    accounts = Account.get_for_user(request.user)

    return render_to_response("account_index.html", { "accounts": accounts }, context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def view(request, id):
    """Lists the transactions in an account"""
    acc = get_object_or_404(Account, pk=id, user=request.user)

    if request.method == 'POST':
        transaction_form = QuickTransactionForm(request.POST)
        if 'account' not in request.POST.keys() or request.POST['account'] != id:
            raise HttpResponseBadRequest
        
        if (transaction_form.is_valid()):
            transaction = transaction_form.save()
            acc = transaction.account
            transaction_form = QuickTransactionForm(initial={ 'account': acc.pk, 'user': request.user.pk })
    else:
        transaction_form = QuickTransactionForm(initial={ 'account': acc.pk, 'user': request.user.pk })

    # Get all the transactions
    transactions = Transaction.objects.select_related().filter(account=acc).order_by('-date', '-date_created')
    
    paginator = Paginator(transactions, 20)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        transactions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        transactions = paginator.page(paginator.num_pages)

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
def edit(request, id):
    """ Edit an account """
    acc = get_object_or_404(Account, pk=id, user=request.user)
    
    orig_balance = acc.balance
    
    if (request.method == 'POST'):
        form = AccountForm(data=request.POST, instance=acc)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.user = request.user
            if orig_balance is not acc.balance:
                acc.set_balance(acc.balance)
            acc.save()
            return redirect(reverse('moneydj.accounts.views.view', args=[acc.pk]))
    else:
        form = AccountForm(instance=acc)
    
    return render_to_response('account_edit.html', {'form': form, 'account': acc}, context_instance=RequestContext(request))

@login_required
def tag_transaction(request, transaction):
    transaction = get_object_or_404(Transaction, pk=transaction, account__user=request.user)
    
    if request.method == "POST" and 'tags' in request.POST.keys():
        transaction.taglink_set.all().delete()
        TagLink.create_relationships(transaction, request.POST['tags'])
        
        # Get the up-to-date set of tags for this transaction and return them
        tags = [{'name': tag.tag.name, 'amount': abs(float(tag.split))} for tag in transaction.taglink_set.select_related().all()]
        return HttpResponse(json.dumps({'transaction': transaction.pk, 'tags': tags, 'total': abs(float(transaction.amount))}), content_type='application/javascript; charset=utf-8')
    else:
        return HttpResponseBadRequest()

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
                tags = tags + u':' + unicode(str(abs(tl.split)))
            tags = tags + u' '
            
        tags = tags.strip()
        data = {
            'date': transaction.date,
            'payee': transaction.payee.name,
            'amount': abs(transaction.amount),
            'credit': int(transaction.amount > 0),
            'transfer': transaction.transfer,
            'tags': tags,
            'account': account.pk,
            'comment': transaction.comment
        }
        form = QuickTransactionForm(initial=data)

    return render_to_response('transaction_edit.html', { 'form': form, 'account': account, 'transaction': transaction }, context_instance=RequestContext(request))

@login_required
def resync(request, account):
    account = get_object_or_404(Account, pk=account, user=request.user)
    account.update_balance(True)
    return redirect(reverse('moneydj.accounts.views.view', args=[account.pk]))

@login_required
def get_payee_suggestions(request):
    """
    Gets all the payees used in transactions by the current user
    """
    if 'q' not in request.GET.keys() or not request.GET['q']:
        return HttpResponseBadRequest()
    
    ts = Payee.objects.select_related().filter(name__icontains=request.GET['q'], transaction__account__user=request.user).distinct().order_by('name')
    
    # Build the array to return as json
    response = [(t.id, t.name) for t in ts]
    
    return HttpResponse(json.dumps(response), content_type='application/javascript; charset=utf-8')

@login_required
def delete_transaction(request, account, transaction):
    transaction = get_object_or_404(Transaction, pk=transaction, account=account, account__user=request.user)
    
    transaction.delete()
    return redirect(reverse('moneydj.accounts.views.view', args=[account]))
