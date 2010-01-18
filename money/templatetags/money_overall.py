from django import template
from moneydj.money.models import Account
import locale

locale.setlocale(locale.LC_ALL, '')

register = template.Library()

@register.inclusion_tag('accounts_block.html')
def accounts_block(user):
    accounts = Account.objects.filter(user=user).order_by('name')
    return {'accounts': accounts}

@register.filter()
def currency(value, symbol):
    return locale.currency(value, grouping=True, symbol=symbol)