from moneydj.accounts.forms import *
from moneydj.money.models import *
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def view(request, id):
    """Lists the transactions in an account"""
    acc = get_object_or_404(Account, pk=id, user=request.user)
    
    # Get all the transactions
    transaction_list = Transaction.objects.filter(account=acc).order_by('-date', '-date_created').select_related()
    
    # Create the paginator
    paginator = Paginator(transaction_list, 25)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        transactions = paginator.page(page)
    except (EmptyPage, InvalidPage):
        transactions = paginator.page(paginator.num_pages)

    return render_to_response('account_view.html', {'account': acc, 'transactions': transactions}, context_instance = RequestContext(request))

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
