# coding=utf-8
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.utils import simplejson
from money.models import Transaction, Account, Payee, TagLink
import datetime
import urllib
from tags.templatetags.tags import cloud
from django.contrib.auth.models import User

class TagLoggedOutTest(TestCase):
    fixtures = ['test_tags']
    def test_index(self):
        index = reverse('tag-index')
        r = self.client.get(index)
        self.assertRedirects(r, reverse('user-login') + '?next=' + urllib.quote(index))
        
    def test_view_tag(self):
        view = reverse('tag-view', args=['food'])
        r = self.client.get(view)
        self.assertRedirects(r, reverse('user-login') + '?next=' + urllib.quote(view))
        
    def test_get_tag_suggestions_bad(self):
        r = self.client.get(reverse('tag-suggestions'))
        self.assertEqual(r.status_code, 400)
        
        r = self.client.get(reverse('tag-suggestions'), data={'q': u''})
        self.assertEqual(r.status_code, 400)
        
    def test_get_tag_suggestions(self):
        r = self.client.get(reverse('tag-suggestions'), data={'q': u'en'})
        self.assertEqual(r.status_code, 200)
        results = simplejson.loads(r.content, 'utf-8')
        self.assertEqual(results, [u'entertainment', u'garden', u'presents'])
        
        # Make sure we get the same results regardless of case
        r = self.client.get(reverse('tag-suggestions'), data={'q': u'EN'})
        self.assertEqual(r.status_code, 200)
        results = simplejson.loads(r.content, 'utf-8')
        self.assertEqual(results, [u'entertainment', u'garden', u'presents'])
        
        # Make sure we get no results for a tag that doesn't exist
        r = self.client.get(reverse('tag-suggestions'), data={'q': u'test'})
        self.assertEqual(r.status_code, 200)
        results = simplejson.loads(r.content, 'utf-8')
        self.assertEqual(results, [])
        
class TagLoggedInTest(TestCase):
    fixtures = ['test_users', 'test_tags', 'test_accounts', 'test_payees', 'test_transactions', 'test_taglinks']
    def setUp(self):
        self.client.login(username='bob', password='bob')
    
    def test_index(self):
        """
        Test the index shows untagged transactions
        """
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(name="HMV")
        t = Transaction.objects.create(account=a, mobile=False, payee=p, amount=Decimal('10'), date=datetime.date.today())
        
        r = self.client.get(reverse('tag-index'))
        self.assertEqual(r.status_code, 200)
        
        # Should have only two untagged transaction (including the one we just created)
        self.assertEqual(len(r.context['transactions'].object_list), 2)
        self.assertEqual([tr.id for tr in r.context['transactions'].object_list], [t.id, 340L])
        
    def test_view_tag(self):
        """
        Test the view page shows only transactions for a specific tag
        """
        p = Payee.objects.get(name="HMV")
        a = Account.objects.get(pk=3)
        t = Transaction.objects.create(account=a, mobile=False, payee=p, amount=Decimal('-50'), date=datetime.date.today())
        
        # By creating these tags we should move dvds up the ranking, and add in books
        TagLink.create_relationships(t, 'books cds dvds')
        
        r = self.client.get(reverse('tag-view', args=['books']))
        self.assertEqual(r.status_code, 200)
        
        # Should just be showing the one transaction we added
        self.assertEqual(len(r.context['transactions'].object_list), 1)
        self.assertEqual([tr.id for tr in r.context['transactions'].object_list], [t.id])
        
class TagCloudTest(TestCase):
    # Use subsets of the large test data in order to speed up and simplify the tests
    fixtures = ['test_users', 'test_tags', 'test_accounts', 'test_payees', 'test_transactions_subset', 'test_taglinks_subset']
    
    def test_cloud_noadditions(self):
        """
        Test the cloud with the dataset as-is
        """
        results = cloud(User.objects.get(pk=2))
        self.assertEqual(len(results['cloud']), 7)
        
        for e in results['cloud']:
            for e2 in results['cloud']:
                if e is not e2:
                    self.failUnless(
                        # The signs are opposite when comparing the amounts and vals because 
                        # A greater amount (-2 vs -4) will have a lesser value
                        (e['amount'] <= e2['amount'] and e['val'] >= e2['val']) 
                        or (e['amount'] >= e2['amount'] and e['val'] <= e2['val']), "amounts and values do not match up: comparing %s (%s) and %s (%s)" % (e['amount'], e['val'], e2['amount'], e2['val']))
        
        results = cloud(User.objects.get(pk=2), credit=1)
        self.assertEqual(len(results['cloud']), 2)
        
        for e in results['cloud']:
            for e2 in results['cloud']:
                if e is not e2:
                    self.failUnless(
                        # Now the signs are normal because we're looking at credit
                        (e['amount'] >= e2['amount'] and e['val'] >= e2['val']) 
                        or (e['amount'] <= e2['amount'] and e['val'] <= e2['val']), "amounts and values do not match up: comparing %s (%s) and %s (%s)" % (e['amount'], e['val'], e2['amount'], e2['val']))