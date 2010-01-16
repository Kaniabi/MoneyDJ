from django.forms import ModelForm
from moneydj.money.models import Account

class AccountForm(ModelForm):
    class Meta:
        model = Account
        exclude = ('user', 'balance_updated', 'date_created')
