# coding=utf8
from django import forms
from moneydj.money import widgets
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
    date = forms.DateField(label=_(u'Date'), initial=datetime.date.today(), widget=widgets.UIDateWidget())
    payee = forms.CharField(label=_(u'Payee'), max_length=50)
    amount = forms.DecimalField(label=_(u'Amount'), decimal_places=2, max_digits=8)
    credit = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, _(u'Expense')), (1, _(u'Income'))], initial=0)
    transfer = forms.BooleanField(label=_(u'Transfer'), required=False)
    tags = forms.CharField(label=_(u'Tags'), required=False)
