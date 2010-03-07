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
    amount = forms.DecimalField(label=_(u'Amount'), decimal_places=2, max_digits=8)
    credit = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, _(u'Expense')), (1, _(u'Income'))], initial=0)
    transfer = forms.BooleanField(label=_(u'Transfer'), required=False)
    tags = forms.CharField(label=_(u'Tags'), required=False)
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

        used_tags = []
        
        tr.taglink_set.all().delete()
        
        abs_amount = abs(Decimal(tr.amount))

        # get a list of the tags entered, separated by spaces
        for t in self.cleaned_data['tags'].split(u' '):
            # partition the tag on the last ':' to get any possible split
            name, delim, split = t.rpartition(u':')
            
            if not name and not split:
                continue
            elif not name:
                # We only have a name, but it's put into the split variable because we're partitioning from the right
                name = split
                split = None

            if split != None:
                try:
                    split = float(split)
                    # Use the total amount if the split is invalid
                    if split > abs_amount or split < 0:
                        split = abs_amount
                except (InvalidOperation, TypeError):
                    # The split couldn't be determined
                    split = abs_amount
            else:
                # A split wasn't specified, so we use the total amount
                split = abs_amount
                
            # Make sure we have the right sign!
            if float(tr.amount) < 0:
                split = -abs(split)
            
            # Convert the split into a string
            split = '%s' % split

            # If name is in the used_tags array, we've already tagged this transaction with that tag
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

        return tr