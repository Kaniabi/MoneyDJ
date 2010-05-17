# coding=utf-8
from django.core import serializers
from django.core.serializers.base import DeserializedObject
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

class SyncTest(TestCase):
    fixtures = ['test_users', 'test_accounts']
    
    def test_accounts_logged_out_bad(self):
        async = reverse('sync-accounts')
        r = self.client.get(async, {'username': 'bob', 'password': 'bob'})
        self.assertEqual(r.status_code, 400)
        
        r = self.client.post(async, {'username': 'bob'})
        self.assertEqual(r.status_code, 400)
        
        r = self.client.post(async, {'password': 'bob'})
        self.assertEqual(r.status_code, 400)
        
        r = self.client.post(async)
        self.assertEqual(r.status_code, 400)
        
        r = self.client.post(async, {'username': 'test', 'password': 'test'})
        self.assertEqual(r.status_code, 403)
        
        r = self.client.post(async, {'username': 'bob', 'password': 'wrong'})
        self.assertEqual(r.status_code, 403)
    
    def accounts_test_helper(self, r, accounts_count, accounts_ids):
        """
        Allows multiple methods to test the same thing
        """
        # Make sure the right content was returned
        self.assertEqual(r['Content-type'], 'application/javascript; charset=utf-8')
        # We need to do this list comprehension because otherwise we get a generator to work with
        res = [obj for obj in serializers.deserialize('json', r.content)]
        
        # Check we got a list of the right length
        self.assertEqual(len(res), accounts_count)
        
        for a in res:
            self.failUnless(isinstance(a, DeserializedObject) and a.object._meta.object_name is 'Account', str(a) + ' is not a deserialized instance of Account')
            self.failIf(a.object.id not in accounts_ids, str(a.object) + " is not one of the allowed accounts")
    
    def test_accounts_logged_out(self):
        """
        Tests the account synchronisation when logged out
        """
        r = self.client.post(reverse('sync-accounts'), {'username': 'bob', 'password': 'bob'})
        self.assertEqual(r.status_code, 200)
        
        self.accounts_test_helper(r, 2, (1, 4))
    
    def test_accounts_logged_in(self):
        """
        Tests the account synchronisation when logged in
        """
        self.client.login(username='fred', password='fred')
        
        r = self.client.get(reverse('sync-accounts'))
        self.assertEqual(r.status_code, 200)
        self.accounts_test_helper(r, 3, (2, 3, 5))
        
        self.client.logout()
        
    def test_transactions_logged_out_bad(self):
        self.fail("Test not completed")
    
    def test_transactions_logged_out(self):
        self.fail("Test not completed")
    
    def test_transactions_logged_in_bad(self):
        self.fail("Test not completed")
    
    def test_transactions_logged_in(self):
        self.fail("Test not completed")