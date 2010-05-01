# coding=utf8
from django import forms
from django.db import transaction, IntegrityError
from django.http import Http404
from django.utils.translation import ugettext as _
from money import widgets
from money.models import *
from decimal import Decimal, InvalidOperation

class AccountForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=[(u'£', u'GBP (£)')])
    bank = forms.ModelChoiceField(queryset=Bank.objects.all().order_by('name'), empty_label=_('None'), required=False)
    error_css_class = 'error'
    required_css_class = 'required'
    class Meta:
        model = Account
        exclude = ('user', 'starting_balance', 'balance_updated', 'date_created')

@transaction.commit_on_success
class QuickTransactionForm(forms.Form):
    date = forms.DateField(label=_(u'Date'), initial=datetime.date.today(), widget=widgets.UIDateWidget())
    payee = forms.CharField(label=_(u'Payee'), max_length=50)
    payee_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    amount = forms.DecimalField(label=_(u'Amount'), decimal_places=2, max_digits=8, help_text=_('The amount of the transaction. Don\'t worry about putting the sign - we\'ll handle that.'))
    credit = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, _(u'Expense')), (1, _(u'Income'))], initial=0)
    transfer = forms.BooleanField(label=_(u'Transfer'), required=False, help_text=_('Is the transaction a transfer between accounts? This will prevent the transaction from appearing in tag reports.'))
    tags = forms.CharField(label=_(u'Tags'), required=False, help_text=_(u'Separate tags using spaces. Use up and down arrows to select a tag suggestion, and press enter to select it. To add splits, follow the tag with a colon and then the amount of the split. You can mix split and normal tags e.g. "food:23.56 cds:9.99 household:3.84 shopping"'))
    account = forms.IntegerField(widget=forms.HiddenInput)
    comment = forms.CharField(label=_(u'Comment'), widget=forms.Textarea(), required=False)
    error_css_class = 'error'
    required_css_class = 'required'

    def save(self, instance=None):
        # Check the instance we've been given (if any)
        if instance is None:
            tr = Transaction()
        elif isinstance(instance, Transaction):
            tr = instance
        else:
            raise TypeError("instance is not a Transaction")

        payee = None
        
        if self.cleaned_data['payee_id']:
            # Try to find a payee with the ID that's been put in the hidden payee id field
            try:
                payee = Payee.objects.get(pk=self.cleaned_data['payee_id'])
            except Payee.DoesNotExist:
                pass
        
        if not payee:
            # Try to find an existing payee with that name
            try:
                payee = Payee.objects.get(name__iexact=self.cleaned_data['payee'])
            except Payee.DoesNotExist:
                # Create a new payee
                payee = Payee(name=self.cleaned_data['payee'])
                payee.save()

        tr.payee = payee

        try:
            acc = Account.objects.get(pk=self.cleaned_data['account'])
        except Account.DoesNotExist:
            raise Http404

        tr.account = acc
        tr.transfer = self.cleaned_data['transfer']
        tr.comment = self.cleaned_data['comment']

        # The credit field returns one or zero
        if (self.cleaned_data['credit'] == u'1'):
            tr.amount = '%s' % abs(float(self.cleaned_data['amount']))
        else:
            tr.amount = '%s' % (-abs(float(self.cleaned_data['amount'])))

        tr.date = self.cleaned_data['date']
        tr.save()

        #
        # Now to deal with the tags
        #        
        tr.taglink_set.all().delete()

        # get a list of the tags entered, separated by spaces
        TagLink.create_relationships(tr, self.cleaned_data['tags'])

        return tr
