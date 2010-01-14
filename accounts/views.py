from django.forms import ModelForm
from moneydj.money.models import *
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.core.urlresolvers import reverse

def view(request, id):
    acc = get_object_or_404(Account, pk=id, user=request.user)
    transactions = Transaction.objects.filter(account=acc).order_by('date')[:10]
    return render_to_response('accounts/view.html', {'account': acc, 'transactions': transactions}, context_instance = RequestContext(request))

def add(request):
    if (request.method == 'POST'):
        form = AccountForm(request.POST)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.user = request.user
            acc.balance_updated = datetime.datetime.today()
            acc.save()
            return redirect(reverse('moneydj.money.views.accounts.view', args=[acc.id]))
    else:
        form = AccountForm()
    return render_to_response('accounts/add.html', {'form': form}, context_instance = RequestContext(request))

class AccountForm(ModelForm):
    class Meta:
        model = Account
        exclude = ('user', 'balance_updated', 'date_created')