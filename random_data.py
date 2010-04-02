from django.core.management import setup_environ
import settings
from decimal import Decimal

setup_environ(settings)

from money.models import Account
import random
import datetime
from accounts.forms import QuickTransactionForm

def weighted_choice(items):
    """
    Gets an item (dict) from the array of items based on its freq attribute
    Credit: http://stackoverflow.com/questions/526255/probability-distribution-in-python/526300#526300
    """
    weight_total = sum((item['freq'] for item in items))
    n = random.uniform(0, weight_total)
    for item in items:
        if n < item['freq']:
            return item
        n = n - item['freq']
    return item

def random_date(start, end):
    """
    This function will return a random datetime between two datetime objects.
    Credit: http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates/553448#553448
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + datetime.timedelta(seconds=random_second))

payees = [{
    'name': 'Sainsbury\'s',
    'tags': ['food', 'household'],
    'min': 0,
    'max': 150,
    'freq': 0.7
},
{
    'name': 'Homebase',
    'tags': ['household', 'garden'],
    'min': 10,
    'max': 70,
    'freq': 0.1
},
{
    'name': 'npower',
    'tags': ['electricity'],
    'min': 25,
    'max': 80,
    'freq': 0.3
},
{
    'name': 'British Gas',
    'tags': ['gas'],
    'min': 25,
    'max': 80,
    'freq': 0.3
},
{
    'name': 'Tesco\'s',
    'tags': ['food', 'household'],
    'min': 0,
    'max': 150,
    'freq': 0.7
},
{
    'name': 'HMV',
    'tags': ['entertainment', 'cds', 'dvds', 'presents', 'birthdays'],
    'min': 3,
    'max': 50,
    'freq': 0.4
},
{
    'name': 'Wagamama',
    'tags': ['food', 'birthdays'],
    'min': 8,
    'max': 50,
    'freq': 0.2
},
{
    'name': 'Nando\'s',
    'tags': ['food', 'birthdays'],
    'min': 8,
    'max': 50,
    'freq': 0.2
},
{
    'name': 'Work',
    'tags': ['work'],
    'min': 800,
    'max': 1200,
    'freq': 0.3,
    'credit': 1
}
]

now = datetime.datetime.now()
max_date = now - datetime.timedelta(seconds=(60 * 60 * 24))
min_date = now - datetime.timedelta(seconds=(60 * 60 * 24 * 365))

print "Max date:", max_date
print "Min date:", min_date

for account in Account.objects.select_related().all():
    t_count = random.randint(50, 100)
    print 'Creating %d transactions for' % t_count, account.name
    
    for i in range(0, t_count):
        payee = weighted_choice(payees)
        
        tags = ' '.join(random.sample(payee['tags'], random.randint(1, len(payee['tags']))))
        
        if 'credit' in payee.keys():
            credit = payee['credit']
        else:
            credit = 0
        
        data = {
            'payee': payee['name'],
            'amount': Decimal('%.2f' % (random.randint(payee['min'], payee['max']) + round(random.random(), 2))),
            'tags': tags,
            'date': random_date(min_date, max_date),
            'account': account.pk,
            'credit': credit
        }
        
        form = QuickTransactionForm(data=data)
        
        if form.is_valid():
            form.save()
        else:
            print 'ERROR creating transaction:', ', '.join(form.errors)