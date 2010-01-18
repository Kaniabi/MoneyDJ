# Create your views here.
from django.shortcuts import render_to_response
from moneydj.money.models import Transaction, Account
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    latest_transactions = Transaction.objects.filter(account__user=request.user).order_by('-date')[:5]
    return render_to_response('dashboard.html', {'transactions': latest_transactions})