from django import template
from money.models import Account, Transaction
from django.db.models import Sum
import locale
from django.utils.dateformat import DateFormat
import datetime
from django.conf import settings
from django.utils.translation import gettext as _
from money.templatetags.money_overall import currency

locale.setlocale(locale.LC_ALL, '')

register = template.Library()

@register.inclusion_tag('report_table.html')
def net_worth_by_time(user, time=None, account=None):
    
    if type(account) is Account and account.user is user:
        transactions = Transaction.objects.filter(account=account)
    else:
        transactions = Transaction.objects.filter(account__user=user)
    
    print time
    
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
    else:
        extra = {'time': 'CONCAT(YEAR(`date`), MONTH(`date`))'}
        
    credit = transactions.filter(credit=True).extra(select=extra).values('time').annotate(Sum('amount')).order_by('time')
    debit = transactions.filter(credit=False).extra(select=extra).values('time').annotate(Sum('amount')).order_by('time')
    
    # Convert the result sets into dictionaries of time: result so we can easily compare the two
    credit = dict([(str(t['time']), t) for t in credit])
    debit = dict([(str(t['time']), t) for t in debit])
    
    # Create a dictionary of time: total values to use in the table
    total = dict([(str(time), t['amount__sum'] - debit[time]['amount__sum']) for time, t in credit.iteritems()])
    
    body = []
    head = []
    values = []
    for t, amount in total.iteritems():
        if time is 'day':
            t = {1: _(u'Sunday'),
             2: _(u'Monday'),
             3: _(u'Tuesday'),
             4: _(u'Wednesday'),
             5: _(u'Thursday'),
             6: _(u'Friday'),
             7: _(u'Saturday'),
             }[t]
        elif time is 'week':
            t = str(t)
            print t
            year = t[:4]
            week = t[4:]
            print year, week
            date = iso_to_gregorian(int(year), int(week), 1)
            df = DateFormat(date)
            t = df.format(settings.SHORT_DATE_FORMAT)
        elif time is 'year':
            # Don't do anything because we already have the year which is what we need
            t = unicode(str(t))
        else:
            # Split the string into year and month, then format it nicely
            year = int(t[:4])
            month = int(t[4:])
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
        head.append(t)
        values.append(currency(amount))
    body.append({'values': values})
    
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