from django import template
from moneydj.money.models import Account
import locale

locale.setlocale(locale.LC_ALL, '')

register = template.Library()

@register.inclusion_tag('accounts_block.html')
def accounts_block(user):
    accounts = Account.get_for_user(user)
    return {'accounts': accounts}

@register.simple_tag
def currency(value, symbol=None, sign=0):
    if sign is 0:
        value = abs(value)
    return locale.currency(value, grouping=True, symbol=symbol)

@register.inclusion_tag('pagination_links.html')
def pagination_links(items):
    return {'items': items}
