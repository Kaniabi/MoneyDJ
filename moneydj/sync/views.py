# coding=utf8
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.models import check_password
from moneydj.money.models import Account, Transaction, Payee
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
import datetime
try:
    import json
except ImportError:
    from django.utils import simplejson as json

# Create your views here.
def get_accounts(request):
    """ Gets a JSON object containing the user's accounts """
    if (request.method != 'POST' or 'username' not in request.POST.keys() or 'password' not in request.POST.keys()) and request.user.is_anonymous():
        return HttpResponseBadRequest(u"Either you didn't POST and you aren't logged in or you didn't give your username and your password")
    
    if not request.user.is_anonymous():
        user = request.user
    else:
        try:
            user = User.objects.get(username=request.POST['username'])
        except User.DoesNotExist:
            return HttpResponseForbidden()
        
        if not check_password(request.POST['password'], user.password):
            return HttpResponseForbidden()
    
    return HttpResponse(serializers.serialize('json', Account.objects.filter(user=user), ensure_ascii=False), content_type='application/javascript; charset=utf-8')

@transaction.commit_on_success
def get_transactions(request):
    # Check the validity of the request
    if request.method != u'POST' or 'username' not in request.POST.keys() or 'password' not in request.POST.keys() or 'transactions' not in request.POST.keys():
        return HttpResponseBadRequest(u"Either you didn't POST or you didn't give your username and your password")
    
    try:
        user = User.objects.get(username=request.POST['username'])
    except User.DoesNotExist:
        return HttpResponseForbidden()

    # Check the username and password given
    if not check_password(request.POST['password'], user.password):
        return HttpResponseForbidden()
    
    # Set up some variables
    accounts = {}
    # errors will contain a list of integers corresponding to the transaction's number
    # That way, clients can determine which transactions were successfully received and 
    # committed to the database
    errors = []
    
    try:
        transactions = json.loads(request.POST['transactions'])
    except ValueError:
        # We couldn't get a valid JSON object
        return HttpResponseBadRequest(u'Could not load the transactions as a JSON object')
    
    if type(transactions) is not list:
        return HttpResponseBadRequest(u'Transactions is not a list')
    
    # Turn signal listening off so that account balances aren't updated
    Transaction.listen_off()
    
    # Go through each transaction we've been sent
    for i in range(len(transactions)):
        if type(transactions[i]) is not dict:
            return HttpResponseBadRequest(u'Element %d of transactions is not a dictionary' % i)
        
        # If we don't have an account, we can't do anything
        if 'account' not in transactions[i].keys():
            errors.append(i)
            continue
        else:
            # If we already know about this account, we can get if from the 'cache'
            if transactions[i]['account'] in accounts.keys():
                account = accounts[transactions[i]['account']]
            else:
                # Otherwise we need to try and find it from the database
                try:
                    account = Account.objects.get(pk=transactions[i]['account'])
                    accounts[account.id] = account
                except Account.DoesNotExist:
                    # If it doesn't appear in the database, add the transaction's number
                    # to the list of errors and continue
                    errors.append(i)
                    continue
        
        # Make sure we have enough information to continue
        if 'payee' not in transactions[i].keys() or 'amount' not in transactions[i].keys():
            errors.append(i)
            continue
        
        # Set up the new Transaction
        t = Transaction(mobile=True, account=account, transfer=False)
        
        # Get the payee's name and make sure it's UTF8
        pname = transactions[i]['payee']
        if type(pname) is str:
            pname = pname.decode('utf-8')
            
        # Try to find an existing payee with that name
        try:
            payee = Payee.objects.get(name__iexact=pname)
        except Payee.DoesNotExist:
            # Create a new payee
            payee = Payee(name=pname)
            payee.save()

        t.payee = payee
        t.amount = '%s' % transactions[i]['amount']
        
        # If credit doesn't appear in the keys, assume it's a negative value
        if 'credit' not in transactions[i].keys():
            t.amount = '%s' % (-abs(float(t.amount)))
        else:
            # Otherwise if credit is anything but 0 assume it's a positive value
            if transactions[i]['credit'] == 0:
                t.amount = '%s' % (-abs(float(t.amount)))
            else:
                t.amount = '%s' % abs(float(t.amount))
        
        # Try to get the date from the POSTed values
        try:
            t.date = datetime.date.fromtimestamp(float(transactions[i]['date']))
        except KeyError, ValueError:
            # KeyError means we don't have one in the POST data
            # ValueError means we couldn't decode it
            t.date = datetime.date.today()
            
        # If we have a comment, decode it
        if 'comment' in transactions[i].keys():
            comment = transactions[i]['comment']
            if type(comment) is str:
                comment = comment.decode('utf-8')
            t.comment = comment
            
        t.save()
    
    # Turn signal listening back on
    Transaction.listen_on()
    
    # Now we can update the balance of all the accounts we've dealt with
    for a in accounts:
        accounts[a].update_balance()
    
    return HttpResponse(json.dumps({'errors': errors}), content_type='application/javascript; charset=utf-8')