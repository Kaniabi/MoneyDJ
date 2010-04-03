# coding=utf-8
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
import urllib

class MoneyUserLoggedOutTest(TestCase):
    def test_register(self):
        r = self.client.get(reverse('user-register'))
        self.assertEqual(r.status_code, 200)
        
    def test_profile(self):
        r = self.client.get(reverse('user-profile'))
        self.assertRedirects(r, reverse('user-login') + '?next=' + urllib.quote(reverse('user-profile')))
        
class MoneyUserLoggedInTest(TestCase):
    fixtures = ['default_data']
    
    def setUp(self):
        self.client.login(username='bob', password='bob')
    
    def test_register(self):
        r = self.client.get(reverse('user-register'))
        self.assertRedirects(r, reverse('dashboard'))