from django.contrib.auth.models import User
from django.template.context import RequestContext
from django.test import TestCase
from django.test.client import Client
from money.models import Account
import urllib
from django.core.paginator import Page

class LoggedOutAccountsTest(TestCase):
    """
    Tests the system with a logged out user
    """
    def _test_redirect(self, url):
        response = self.client.get(url)
        self.assertRedirects(response, expected_url='/user/login/?next=' + urllib.quote(url))
    
    def test_index(self):
        self._test_redirect('/accounts/')
        
    def test_view(self):
        self._test_redirect('/accounts/1/')
        
    def test_add(self):
        self._test_redirect('/accounts/add/')
    
    def test_edit(self):
        self._test_redirect('/accounts/1/edit/')
    
    def test_tag_transaction(self):
        self._test_redirect('/accounts/transaction/1/tag/')
    
    def test_edit_transaction(self):
        self._test_redirect('/accounts/1/transaction/1/')
    
    def test_resync(self):
        self._test_redirect('/accounts/1/resync/')
    
    def test_delete_transaction(self):
        self._test_redirect('/accounts/1/transaction/1/delete/')
        
    def test_get_payee_suggestions(self):
        self._test_redirect('/accounts/payee/suggest/?q=sain')
        
class BobAccountsTest(TestCase):
    """
    Tests the accounts application with a logged in user
    """
    fixtures = ['default_data.json']
    
    def setUp(self):
        self.client.login(username='bob', password='bob') or self.fail('Could not log in as Bob')
        self.user = User.objects.get(username='bob')
        
    def test_index(self):
        response = self.client.get('/accounts/')
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
        
    def test_view_own(self):
        response = self.client.get('/accounts/1/')
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
            for t in response.context['transactions'].object_list:
                self.assertEquals(t.account, a)
        except KeyError:
            self.fail('transactions is not in the template context')
        
        # Make sure we're using the RequestContext
        try:
            response.context['user']
        except KeyError:
            self.fail('Not using RequestContext')