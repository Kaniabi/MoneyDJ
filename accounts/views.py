from decimal import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from moneydj.accounts.forms import *
from moneydj.money.models import *

@transaction.commit_on_success
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

            # The credit field returns one or zero, but we need a boolean value for the model
            if (transaction_form.cleaned_data['credit'] == u'1'):
                tr.credit = True
            else:
                tr.credit = False

            tr.date = transaction_form.cleaned_data['date']
            tr.save()

            #
            # Now to deal with the tags
            #

            used_tags = []

            # get a list of the tags entered, separated by spaces
            for t in transaction_form.cleaned_data['tags'].split(u' '):
                # partition the tag on the last ':' to get any possible split
                name, delim, split = t.rpartition(u':')

                if not name and not split:
                    continue
                elif not name:
                    name = split
                    split = None

                if split != None:
                    try:
                        split = Decimal(split)
                        # Use the total amount if the split is invalid
                        if split > tr.amount or split < 0:
                            split = tr.amount
                    except:
                        # The split couldn't be determined
                        split = tr.amount
                else:
                    # A split wasn't specified, so we use the total amount
                    split = tr.amount

                if name in used_tags:
                    continue
                else:
                    try:
                        tag = Tag(name=name)
                        tag.save()
                        used_tags.append(name)
                    except IntegrityError:
                        tag = Tag.objects.filter(name__iexact=name)[0]
                        used_tags.append(name)

                rel = TagLink(tag=tag, transaction=tr, split=split)
                rel.save()

            acc.update_balance()
            transaction_form = QuickTransactionForm()
    else:
        transaction_form = QuickTransactionForm()

    # Get all the transactions
    transactions = Transaction.objects.filter(account=acc).order_by('-date', '-date_created').select_related()

    return render_to_response('account_view.html', {
        'account': acc,
        'transactions': transactions,
        'transaction_form': transaction_form
    }, context_instance=RequestContext(request))

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

def add_transaction(request, account):
    """Adds a transaction to the specified account"""
    pass

def view_transaction(request, account, transaction):
    """Views a transaction"""
    pass
