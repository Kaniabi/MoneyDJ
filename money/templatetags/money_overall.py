from django import template
from moneydj.money.models import Account

register = template.Library()

@register.inclusion_tag('accounts_block.html')
def accounts_block(user):
    accounts = Account.objects.filter(user=user).order_by('name')
    return {'accounts': accounts}