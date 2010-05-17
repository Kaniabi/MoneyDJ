from django import template
from moneydj.money.models import TagLink, Account
from django.db.models import Sum
from django.contrib.auth.models import User
import operator

register = template.Library()

@register.inclusion_tag('tag_cloud.html')
def cloud(account_user=None, credit=0, number=20):
    items = TagLink.objects.values('tag__name').annotate(total=Sum('split'))

    if credit is 0:
        items = items.filter(total__lt=0)
    else:
        items = items.filter(total__gt=0)

    if isinstance(account_user, Account):
        items = items.filter(transaction__account=account_user, transaction__transfer=False)
    elif isinstance(account_user, User):
        items = items.filter(transaction__account__user=account_user, transaction__transfer=False)
    else:
        return {'cloud': []}

    items = items.order_by('total', 'tag__name')[:number]

    if len(items) < 2:
        c = []
        if len(items) is 1:
            c.append({'name': items[0]['tag__name'], 'val': 10, 'amount': items[0]['total']})
        return {'cloud': c}

    cloud = []
    max = 0
    min = 0

    # Figure out the max and min values
    for i in items:
        if i['total'] > max:
            max = i['total']
        if i['total'] < min or min == 0:
            min = i['total']

    # If we're looking at all items where money is going out, swap over the 
    # max and min values as the max will be the lowest possible (negative) number 
    if not credit:
        max, min = min, max

    diff = max - min

    for i in items:
        percent = (i['total'] - min) / diff
        cloud.append({'name': i['tag__name'],
                      # Distribute the cloud over 10 levels of granularity
                      'val': int(round(percent * 9) + 1),
                      'amount': i['total']})

    # Sort the cloud by the tag name
    cloud.sort(key=operator.itemgetter('name'))

    return {'cloud': cloud}
