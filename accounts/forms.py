# coding=utf8
from django import forms
import datetime
from moneydj.money.models import Account, Transaction
from django.utils.translation import ugettext as _

class AccountForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=[(u'£', u'GBP (£)'), (u'€', u'EUR (€)')])
    error_css_class = 'error'
    required_css_class = 'required'
    class Meta:
        model = Account
        exclude = ('user', 'starting_balance', 'balance_updated', 'date_created')

class QuickTransactionForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today())
    payee = forms.CharField(max_length=50)
    amount = forms.DecimalField(decimal_places=2,max_digits=8)
    credit = forms.ChoiceField(widget=forms.RadioSelect, choices=[(False, _(u'Expense')), (True, _(u'Income'))], initial=False)
    transfer = forms.BooleanField(label=_(u'Transfer'), required=False)