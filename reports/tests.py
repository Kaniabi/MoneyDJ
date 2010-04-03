# coding=utf-8
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
import urllib
from django.contrib.auth.models import User
from reports.templatetags.reports_tags import net_worth_by_time

class ReportsLoggedOutTest(TestCase):
    def test_index(self):
        index = reverse('reports-index')
        r = self.client.get(index)
        self.assertRedirects(r, reverse('user-login') + '?next=' + urllib.quote(index))
        
class ReportsLoggedInTest(TestCase):
    fixtures = ['default_data']
    def setUp(self):
        self.client.login(username='bob', password='bob')
    
    def test_index(self):
        r = self.client.get(reverse('reports-index'))
        self.assertEqual(r.status_code, 200)
        
class ReportsTagsTest(TestCase):
    fixtures = ['default_data']
    
    def test_net_worth_by_time(self):
        u = User.objects.get(pk=3)
        
        # Make sure invalid time values raise a ValueError
        self.failUnlessRaises(ValueError, lambda: net_worth_by_time(u, 'time'))
        
        # The expected values for the net worth by month report
        expected = {'report': {
            'body': [{
                'head': u"Fred's Current Account",
                'values': [
                    '1,523.47',
                    '-115.16',
                    '-161.76',
                    '-939.02',
                    '477.91',
                    '-78.74',
                    '492.73',
                    '809.49',
                    '529.47',
                    '712.47',
                    '858.01',
                    '665.71',
                    '0.00'
                    ]
                }, {
                'head': u"Fred's Savings Account",
                'values': [
                    '-696.38',
                    '491.96',
                    '-223.93',
                    '782.96',
                    '-592.81',
                    '-315.56',
                    '725.51',
                    '830.50',
                    '-113.61',
                    '-394.57',
                    '461.71',
                    '1,803.30',
                    '-120.87'
                    ]
                }],
            'head': [
                u'Apr 2009',
                u'May 2009',
                u'Jun 2009',
                u'Jul 2009',
                u'Aug 2009',
                u'Sep 2009',
                u'Oct 2009',
                u'Nov 2009',
                u'Dec 2009',
                u'Jan 2010',
                u'Feb 2010',
                u'Mar 2010',
                u'Apr 2010',
                ]
        }}
        
        results = net_worth_by_time(u, 'month')
        
        self.assertEqual(results, expected)
        
        # The expected results of the day of the week report
        expected = {'report': {
            'body': [{
                'head': u"Fred's Current Account",
                'values': [
                    '2,183.81',
                    '-469.40',
                    '-258.72',
                    '2,419.12',
                    '-773.78',
                    '1,118.70',
                    '554.85'
                    ]
                }, {
                'head': u"Fred's Savings Account",
                'values': [
                    '910.14',
                    '-457.75',
                    '392.20',
                    '1,579.57',
                    '452.39',
                    '-497.59',
                    '259.25'
                    ]
                }],
            'head': [
                u'Sunday',
                u'Monday',
                u'Tuesday',
                u'Wednesday',
                u'Thursday',
                u'Friday',
                u'Saturday'
                ]
        }}
        
        results = net_worth_by_time(u, 'day')
        
        self.assertEqual(results, expected)