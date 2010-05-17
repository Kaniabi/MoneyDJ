# coding=utf-8

from moneydj.accounts.forms import AccountForm
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.paginator import Page
from django.core.urlresolvers import reverse
from django.test import TestCase
from moneydj.money.models import Account, TagLink
import urllib
import datetime

class LoggedOutAccountsTest(TestCase):
    """
    Tests the system with a logged out user
    """
    def _test_redirect(self, url):
        response = self.client.get(url)
        self.assertRedirects(response, expected_url='/user/login/?next=' + urllib.quote(url))
    
    def test_index(self):
        self._test_redirect(reverse('account-index'))
        
    def test_view(self):
        self._test_redirect(reverse('account-view', args=[1]))
        
    def test_add(self):
        self._test_redirect(reverse('account-add'))
    
    def test_edit(self):
        self._test_redirect(reverse('account-edit', args=[1]))
    
    def test_tag_transaction(self):
        self._test_redirect(reverse('transaction-tag', args=[1]))
    
    def test_edit_transaction(self):
        self._test_redirect(reverse('transaction-edit', args=[1, 1]))
    
    def test_resync(self):
        self._test_redirect(reverse('account-resync', args=[1]))
    
    def test_delete_transaction(self):
        self._test_redirect(reverse('transaction-delete', args=[1, 1]))
        
    def test_get_payee_suggestions(self):
        self._test_redirect(reverse('payee-suggestions'))
        
class BobAccountsTest(TestCase):
    """
    Test the parts of the accounts application that don't require the large data 
    sets (makes it faster!) with a logged in user
    """
    fixtures = ['test_users', 'test_accounts']
    
    def setUp(self):
        self.client.login(username='bob', password='bob') or self.fail('Could not log in as Bob')
        self.user = User.objects.get(username='bob')
        
    def test_index(self):
        """
        Tests the content of the index page
        """
        response = self.client.get(reverse('account-index'))
        self.assertEquals(response.status_code, 200)
        
        # Check that two accounts were passed to the template
        try:
            self.assertEquals(len(response.context['accounts']), 2)
        except KeyError:
            self.fail('accounts is not in the template context')
        
        # Make sure each account actually belongs to this user
        for a in response.context['accounts']:
            self.assertEquals(a.user, self.user)
        
        # Make sure we're using the RequestContext
        try:
            response.context['user']
        except KeyError:
            self.fail('Not using RequestContext')
            
    def test_view_other(self):
        """
        Makes sure you cannot view someone else's accounts
        """
        response = self.client.get(reverse('account-view', args=[3]))
        self.assertEquals(response.status_code, 404)
    
    def test_edit(self):
        """
        Makes sure the edit account page displays properly
        """
        response = self.client.get(reverse('account-edit', args=[1]))
        self.assertEquals(response.status_code, 200)
        
        a = Account.objects.get(pk=1)
        
        # Check we're showing the right account
        try:
            self.assertEquals(response.context['account'], a)
        except KeyError:
            self.fail('account is not in the template context')
        
        # Make sure we're using the AccountForm
        try:
            self.failUnless(isinstance(response.context['form'], AccountForm), "The form is not an AccountForm")
        except KeyError:
            self.fail('Not using a form')
        
        # Make sure we're using the RequestContext
        try:
            response.context['user']
        except KeyError:
            self.fail('Not using RequestContext')
        
    def test_edit_other(self):
        """
        Makes sure you cannot edit someone else's accounts
        """
        response = self.client.get(reverse('account-edit', args=[3]))
        self.assertEquals(response.status_code, 404)
        
    def test_tag_transaction_other(self):
        """
        Ensures you can't tag someone else's transaction
        """
        response = self.client.post(reverse('transaction-tag', args=[103]), {'tags': 'cds:15 dvds:12:37 presents birthdays entertainment'})
        self.assertEquals(response.status_code, 404)
        
    def test_get_payee_suggestions_bad(self):
        """ Makes sure that requests for payee suggestions that are malformed are rejected """
         
        response = self.client.get(reverse('payee-suggestions'), {})
        self.assertEquals(response.status_code, 400)
        
        response = self.client.post(reverse('payee-suggestions'), {'q': 'work'})
        self.assertEquals(response.status_code, 400)
        
class BobAccountsTransactionsTest(TestCase):
    """
    Tests the parts of the accounts application that require the large data sets
    with a logged in user
    """
    fixtures = ['test_users', 'test_accounts', 'test_payees', 'test_transactions']
    
    def setUp(self):
        self.client.login(username='bob', password='bob') or self.fail('Could not log in as Bob')
        self.user = User.objects.get(username='bob')
        
    def test_view_own(self):
        response = self.client.get(reverse('account-view', args=[1]))
        self.assertEquals(response.status_code, 200)
        
        a = Account.objects.get(pk=1)
        
        # Check we're showing the right account
        try:
            self.assertEquals(response.context['account'], a)
        except KeyError:
            self.fail('account is not in the template context')
            
        # Check the right transactions have been returned
        try:
            self.failUnless(isinstance(response.context['transactions'], Page), 'transactions are not paginated')
            
            # Make sure every transaction belongs to the currently viewed account
            for t in response.context['transactions'].object_list:
                self.assertEquals(t.account, a)
        except KeyError:
            self.fail('transactions is not in the template context')
        
        # Make sure we're using the RequestContext
        try:
            response.context['user']
        except KeyError:
            self.fail('Not using RequestContext')
        
    def test_view_form(self):
        """
        Tests the form on the view page to make sure it saves correctly
        """
        response = self.client.post(reverse('account-view', args=[1]), {
            'date': datetime.date.today().strftime('%Y-%m-%d'),
            'payee': "Kwik-Fit",
            'amount': "123.54",
            'credit': "0",
            'tags': "car tyres:104",
            'account': "1",
            'comment': ""
        })
        self.assertEqual(response.status_code, 200)
        
        # Make sure the first transaction is the one we just added
        try:
            self.assertEqual(response.context['transactions'].object_list[0].payee.name, "Kwik-Fit")
        except KeyError:
            self.fail('transactions is not in the template context')
        
        a = Account.objects.get(pk=1)
        
        # Check the balance of the Account has been updated
        self.assertEqual(a.balance, Decimal('3578.01'))
        
    def test_tag_transaction_bad(self):
        """
        Makes sure the tag_transaction view only accepts the properly formatted request
        """
        response = self.client.post(reverse('transaction-tag', args=[1]), {})
        self.assertEquals(response.status_code, 400)
        
        response = self.client.get(reverse('transaction-tag', args=[1]), {'tags': 'work income'})
        self.assertEquals(response.status_code, 400)
        
    def test_tag_transaction(self):
        """
        Tests the tag_transaction view
        """
        response = self.client.post(reverse('transaction-tag', args=[1]), {'tags': 'work income:50 other:'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/javascript; charset=utf-8')
        
        tags = TagLink.objects.filter(transaction=1)
        
        # Make sure the right number of tag links has been created
        self.assertEquals(len(tags), 3)
        
        # Make sure the right tag links has been created
        self.assertEquals(unicode(tags[0]), u'Work - work')
        self.assertEquals(tags[0].split, Decimal('827.59'))
        self.assertEquals(unicode(tags[1]), u'Work - income')
        self.assertEquals(tags[1].split, Decimal('50.00'))
        self.assertEquals(unicode(tags[2]), u'Work - other')
        # This tag was malformed so it should just be the full amount
        self.assertEquals(tags[2].split, Decimal('827.59'))
            
    def test_edit_post(self):
        """
        Makes sure the edit account form works properly
        """
        orig_a = Account.objects.get(pk=1)
        
        balance = orig_a.balance - 500
        
        response = self.client.post(reverse('account-edit', args=[1]), {
                'name': u"Bob's Updated Account",
                'number': u'',
                'sort_code': u'',
                'bank': u'',
                'currency': u'£',
                'balance': balance
            })
        self.assertRedirects(response, reverse('account-view', args=[1]))
        
        a = Account.objects.get(pk=1)
        
        # Check all the attributes got updated properly
        self.assertEquals(a.name, u"Bob's Updated Account")
        self.assertEquals(a.track_balance, False)
        self.assertEquals(a.balance, balance)
        self.assertEquals(a.starting_balance, orig_a.starting_balance - 500)
        
    def test_get_payee_suggestions(self):
        """ Tests the payee suggestions view """
         
        response = self.client.get(reverse('payee-suggestions'), {'q': 'work'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/javascript; charset=utf-8')
        
        # Make sure the response contains the right content
        self.assertNotContains(response, text=u"Other Work")
        self.assertContains(response, text="Work")