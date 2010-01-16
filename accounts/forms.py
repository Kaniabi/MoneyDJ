# coding=utf8
from django.forms import ModelForm
from django import forms
from moneydj.money.models import Account

class AccountForm(ModelForm):
    currency = forms.ChoiceField(choices=[(u'£', u'GBP (£)'), (u'€', u'EUR (€)')])
    class Meta:
        model = Account
        exclude = ('user', 'balance_updated', 'date_created')
