from django import template
from django.conf import settings
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from django.utils.translation import gettext as _
from money.models import Account, Transaction
from money.templatetags.money_overall import currency
import datetime
import locale

locale.setlocale(locale.LC_ALL, '')

register = template.Library()

@register.inclusion_tag('report_table.html')
def net_worth_by_time(user, time=None, account=None):
    
    if type(account) is Account and account.user is user:
        transactions = Transaction.objects.select_related().filter(account=account,transfer=False)
    else:
        transactions = Transaction.objects.select_related().filter(account__user=user,transfer=False,account__track_balance=True)
    
    # Day of the week
    if time == 'day':
        extra = {'time': 'DAYOFWEEK(`date`)'}
    # Week number (and year)
    elif time == 'week':
        extra = {'time': 'YEARWEEK(`date`)'}
    # Year
    elif time == 'year':
        extra = {'time': 'YEAR(`date`)'}
    # Month (and year)
    elif time == 'month' or time is None:
        extra = {'time': 'CONCAT(YEAR(`date`), MONTH(`date`))'}
    else:
        raise ValueError, time + ' is not a valid time value'
        
    credit = transactions.extra(select=extra).values('time', 'account__id').annotate(Sum('amount'))
    
    # day needs to be sorted differently than the others because it's a more arbitrary aggregation
    if time == 'day':
        credit = credit.order_by('time')
    else:
        credit = credit.order_by('date')
    
    total = {}
    accounts = []
    times = []
    for t in credit:
        if t['time'] not in times:
            times.append(t['time'])
        
        if t['account__id'] not in accounts:
            accounts.append(t['account__id'])
            
        # Convert the result set into associative dictionaries of account: {time: amount}
        if not total.has_key(t['account__id']):
            total[t['account__id']] = {t['time']: t['amount__sum']}
        else:
            total[t['account__id']][t['time']] = t['amount__sum']
    
    body = []
    head = []
    
    for timekey in times:
        if time == 'day':
            t = {1: _(u'Sunday'),
                 2: _(u'Monday'),
                 3: _(u'Tuesday'),
                 4: _(u'Wednesday'),
                 5: _(u'Thursday'),
                 6: _(u'Friday'),
                 7: _(u'Saturday'),
                 }[int(timekey)]
        elif time == 'week' and len(str(timekey)) > 4:
            timekey = str(timekey)
            year = timekey[:4]
            week = timekey[4:]
            date = iso_to_gregorian(int(year), int(week), 1)
            df = DateFormat(date)
            t = df.format(settings.SHORT_DATE_FORMAT)
        elif time == 'year':
            # Don't do anything because we already have the year which is what we need
            t = unicode(timekey)
        # Month
        elif len(timekey) > 4:
            # Split the string into year and month, then format it nicely
            year = int(timekey[:4])
            month = int(timekey[4:])
            month = {1: _(u'Jan'),
                     2: _(u'Feb'),
                     3: _(u'Mar'),
                     4: _(u'Apr'),
                     5: _(u'May'),
                     6: _(u'Jun'),
                     7: _(u'Jul'),
                     8: _(u'Aug'),
                     9: _(u'Sep'),
                     10: _(u'Oct'),
                     11: _(u'Nov'),
                     12: _(u'Dec')
                     }[month]
            t = month + u' ' + unicode(str(year))
        else:
            continue
        
        # Add the value to the head
        head.append(t)
        
    # Get the accounts
    accounts = dict([(acc.id, acc.name) for acc in Account.objects.filter(id__in=accounts)])
    
    for a in total:
        values = []
        for timekey in times:
            if total[a].has_key(timekey):
                values.append(currency(total[a][timekey], sign=1))
            else:
                values.append(currency(0, sign=1))
        body.append({'values': values, 'head': accounts[a]})
    
    return {'report': {'head': head, 'body': body}}

def iso_year_start(iso_year):
    """
    Works out the date on which the year starts
    From: http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
    """
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    """
    Works out the date given a year, week number and day number (i.e. M=1, T=2, W=3...)
    From: http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
    """
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(iso_day-1, 0, 0, 0, 0, 0, iso_week-1)