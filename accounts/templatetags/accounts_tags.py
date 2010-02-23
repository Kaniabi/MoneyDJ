from django import template

register = template.Library()

@register.inclusion_tag("view_transactions.html")
def show_transactions(transactions):
    return {'transactions': transactions}

@register.inclusion_tag("transaction_row.html")
def transaction_row(t):
    return {'t': t}