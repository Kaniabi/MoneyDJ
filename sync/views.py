# coding=utf8
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.models import check_password
from money.models import Account, Transaction, Payee
from django.core import serializers
from django.contrib.auth.models import User
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
        user = get_object_or_404(User, username=request.POST['username'])
    
        if not check_password(request.POST['password'], user.password):
            return HttpResponseForbidden()
    
    return HttpResponse(serializers.serialize('json', Account.objects.filter(user=user), ensure_ascii=False), content_type='application/javascript; charset=utf-8')

def get_transactions(request):
    if request.method != u'POST' or 'username' not in request.POST.keys() or 'password' not in request.POST.keys() or 'transactions' not in request.POST.keys():
        return HttpResponseBadRequest(u"Either you didn't POST or you didn't give your username and your password")
    
    user = get_object_or_404(User, username=request.POST['username'])

    if not check_password(request.POST['password'], user.password):
        return HttpResponseForbidden()
    
    accounts = {}
    errors = []
    
    try:
        transactions = json.loads(request.POST['transactions'])
    except ValueError:
        # We couldn't get a valid JSON object
        return HttpResponseBadRequest(u'Could not load the transactions as a JSON object')
    
    if type(transactions) is not list:
        return HttpResponseBadRequest(u'Transactions is not a list')
    
    for i in range(len(transactions)):
        if type(transactions[i]) is not dict:
            return HttpResponseBadRequest(u'Element %d of transactions is not a dictionary' % i)
        
        # If we don't have an account, we can't do anything
        if 'account' not in transactions[i].keys():
            errors.append(i)
            continue
        else:
            if transactions[i]['account'] in accounts.keys():
                account = accounts[transactions[i]['account']]
            else:
                try:
                    account = Account.objects.get(pk=transactions[i]['account'])
                    accounts[account.id] = account
                except Account.DoesNotExist:
                    errors.append(i)
                    continue
        
        t = Transaction()
        t.mobile = True
        t.account = account
        
        if 'payee' not in transactions[i].keys() or 'amount' not in transactions[i].keys():
            errors.append(i)
            continue
        
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
        if 'credit' not in transactions[i].keys():
            t.credit = False
        else:
            if transactions[i]['credit'] == 0:
                t.credit = False
            else:
                t.credit = True
        
        if 'date' not in transactions[i].keys():
            t.date = datetime.date.today()
        else:
            t.date = datetime.date.fromtimestamp(float(transactions[i]['date']))
            
        if 'comment' in transactions[i].keys():
            comment = transactions[i]['comment']
            if type(comment) is str:
                comment = comment.decode('utf-8')
            t.comment = comment
            
        t.transfer = False
        t.save()
    
    for a in accounts:
        accounts[a].update_balance()
    
    return HttpResponse(json.dumps({'errors': errors}), content_type='application/javascript; charset=utf-8')