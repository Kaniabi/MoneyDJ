# coding=utf-8
from django.test.testcases import TestCase
from django.core.urlresolvers import reverse
from money.models import Transaction, Account, Payee
from decimal import Decimal
import datetime
import random
from django.db import transaction

class LoggedOutTest(TestCase):
    def test_index(self):
        """
        Ensures redirection to the right page
        """
        r = self.client.get('/')
        self.assertRedirects(r, reverse('user-login'))

class LoggedInTest(TestCase):
    fixtures = ['default_data']
    def setUp(self):
        self.client.login(username='bob', password='bob')
    
    def test_index(self):
        """
        Ensures redirection to the right page
        """
        r = self.client.get('/')
        self.assertRedirects(r, reverse('dashboard'))
        
class TransactionTest(TestCase):
    """
    Tests the transaction class functions
    """
    fixtures = ['default_data']
    
    def test_add_positive(self):
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(pk=1)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('512.78'), date=datetime.datetime.now())
        t.save()
        
        a = Account.objects.get(pk=1)
        
        self.assertEqual(a.balance, Decimal('4214.33'))
        
    def test_add_negative(self):
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(pk=1)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('-512.78'), date=datetime.datetime.now())
        t.save()
        
        a = Account.objects.get(pk=1)
        
        self.assertEqual(a.balance, Decimal('3188.77'))
        
    def test_delete_negative(self):
        Transaction.objects.get(pk=74).delete()
        
        a = Account.objects.get(pk=1)
        
        self.assertEqual(a.balance, Decimal('3738.40'))
        
    def test_delete_positive(self):
        Transaction.objects.get(pk=27).delete()
        
        a = Account.objects.get(pk=1)
        
        self.assertEqual(a.balance, Decimal('2572.07'))
    
    def test_add_lots(self):
        """
        Simulates a synchronisation of a large amount of transactions
        """
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(pk=1)
        
        total = a.balance
        orig = total.copy_abs()
        
        # Turn the signal listening off so we can update the account balance afterwards
        Transaction.listen_off()
        
        for i in range(1, 100):
            amount = Decimal('%.2f' % i)
            if i > 50:
                amount = amount.copy_negate()
            
            t = Transaction(account=a, mobile=False, payee=p, amount=amount, date=datetime.datetime.now())
            t.save()
            
            total += amount
        
        # Turn signal listening back on
        Transaction.listen_on()
        
        a = Account.objects.get(pk=1)
        
        # Make sure the balance hasn't been updated so far
        self.assertEqual(a.balance, orig)
        
        # Update the balance and check it's ok
        a.update_balance(True)
        self.assertEqual(a.balance, total)