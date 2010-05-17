from django import template
from moneydj.money.models import Account
from django.utils.formats import localize

register = template.Library()

@register.inclusion_tag('accounts_block.html')
def accounts_block(user):
    accounts = Account.get_for_user(user)
    return {'accounts': accounts}

@register.simple_tag
def currency(value, symbol=None, sign=0):
    if sign is 0:
        value = abs(value)
    val = unicode(localize(value))
    if symbol is not None:
        val = ''.join([symbol, val])
    return val

@register.inclusion_tag('pagination_links.html')
def pagination_links(items):
    return {'items': items}
