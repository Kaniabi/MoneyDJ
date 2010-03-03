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
        transactions = Transaction.objects.filter(account=account,transfer=False)
    else:
        transactions = Transaction.objects.filter(account__user=user,transfer=False)
    
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
        
    credit = transactions.extra(select=extra).filtervalues('time').annotate(Sum('amount')).order_by('time')
    
    # Convert the result set into dictionaries of time: result
    total = dict([(str(t['time']), t['amount__sum']) for t in credit])
    
    body = []
    head = []
    values = []
    
    # Have to iterate over the sorted keys because dicts don't maintain order
    keys = total.keys()
    keys.sort()
    print keys
    for timekey in keys:
        if time == 'day':
            t = {1: _(u'Sunday'),
                 2: _(u'Monday'),
                 3: _(u'Tuesday'),
                 4: _(u'Wednesday'),
                 5: _(u'Thursday'),
                 6: _(u'Friday'),
                 7: _(u'Saturday'),
                 }[timekey]
        elif time == 'week' and len(timekey) > 4:
            year = timekey[:4]
            week = timekey[4:]
            date = iso_to_gregorian(int(year), int(week), 1)
            df = DateFormat(date)
            t = df.format(settings.SHORT_DATE_FORMAT)
        elif time == 'year':
            # Don't do anything because we already have the year which is what we need
            t = unicode(timekey)
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
        head.append(t)
        values.append(currency(total[timekey]))
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