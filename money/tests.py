# coding=utf-8
from django.test.testcases import TestCase
from django.core.urlresolvers import reverse
from moneydj.money.models import Transaction, Account, Payee, TagLink
from decimal import Decimal
import datetime

class LoggedOutTest(TestCase):
    def test_index(self):
        """
        Ensures redirection to the right page
        """
        r = self.client.get('/')
        self.assertRedirects(r, reverse('user-login'))

class LoggedInTest(TestCase):
    fixtures = ['test_users']
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
    fixtures = ['test_users', 'test_accounts', 'test_payees', 'test_transactions']
    
    def test_add_positive(self):
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(pk=1)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('512.78'), date=datetime.date.today())
        t.save()
        
        a = Account.objects.get(pk=1)
        
        self.assertEqual(a.balance, Decimal('4214.33'))
        
    def test_add_negative(self):
        a = Account.objects.get(pk=1)
        p = Payee.objects.get(pk=1)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('-512.78'), date=datetime.date.today())
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
        
        count = Transaction.objects.all().count()
        
        # Turn the signal listening off so we can update the account balance afterwards
        Transaction.listen_off()
        
        for i in range(1, 100):
            amount = Decimal('%.2f' % i)
            if i > 50:
                amount = amount.copy_negate()
            
            t = Transaction(account=a, mobile=False, payee=p, amount=amount, date=datetime.date.today())
            t.save()
            
            total += amount
            count += 1
        
        # Turn signal listening back on
        Transaction.listen_on()
        
        a = Account.objects.get(pk=1)
        
        # Make sure the balance hasn't been updated
        self.assertEqual(a.balance, orig)
        
        # Make sure the right number of transactions has been added
        self.assertEqual(Transaction.objects.all().count(), count)
        
class AccountTest(TestCase):
    """
    Tests the Account model
    """
    fixtures = ['test_users', 'test_payees', 'test_accounts', 'test_transactions']
    
    def test_update_balance(self):
        # Make sure the Transaction model doesn't update the account
        Transaction.listen_off()
        
        # Delete the first transaction (827.59 of credit)
        t = Transaction.objects.select_related().get(pk=1)
        t.delete()
        a = t.account
        
        # The balance shouldn't have changed
        self.assertEqual(a.balance, Decimal('3701.55'))
        
        # Update the balance, only taking into account new transactions
        a.update_balance(all=False)
        
        # The balance still shouldn't have changed
        self.assertEqual(a.balance, Decimal('3701.55'))
        
        # Create a new transaction
        p = Payee.objects.get(pk=1)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('300'), date=datetime.date.today())
        t.save()
        
        # Update the balance once more
        a.update_balance(all=False)
        
        # The balance should now be +300 from the added transaction
        self.assertEqual(a.balance, Decimal('4001.55'))
        
        # Update the balance a final time
        a.update_balance(all=True)
        
        # The balance should now be completely up-to-date
        self.assertEqual(a.balance, Decimal('3173.96'))
        
        # Turn transaction listening back on for other tests
        Transaction.listen_on()
        
    def test_set_balance(self):
        # Test with a float
        a = Account.objects.get(pk=1)
        a.set_balance(3801.55)
        self.assertEqual(a.starting_balance, Decimal('1100.00'))
        
        # Now with a Decimal object
        a = Account.objects.get(pk=1)
        a.set_balance(Decimal('3801.55'))
        self.assertEqual(a.starting_balance, Decimal('1100.00'))
        
        # Finally with a string
        a = Account.objects.get(pk=1)
        a.set_balance('3801.55')
        self.assertEqual(a.starting_balance, Decimal('1100.00'))
        
class TagLinkTest(TestCase):
    """
    Tests the TagLink model
    """
    fixtures = ['test_users', 'test_accounts', 'test_payees', 'test_tags']
    
    def test_create_relationships(self):
        a = Account.objects.get(pk=4)
        p = Payee.objects.get(pk=5)
        t = Transaction(account=a, mobile=False, payee=p, amount=Decimal('-50'), date=datetime.date.today())
        t.save()
        
        TagLink.create_relationships(t, u' food:26.30 toiletries:12.98\n household:51.23')
        
        expected = [{
            'name': 'food',
            'split': Decimal('-26.30')
        }, {
            'name': 'toiletries',
            'split': Decimal('-12.98')
        }, {
            'name': 'household',
            'split': Decimal('-50')
        }]
        
        results = TagLink.objects.select_related().filter(transaction=t).order_by('id')
        
        self.assertEqual(len(results), len(expected))
        
        for t in range(len(results)):
            self.assertEqual(results[t].tag.name, expected[t]['name'])
            self.assertEqual(results[t].split, expected[t]['split'])
            
class PayeeTest(TestCase):
    """
    Tests the Payee model
    """
    fixtures = ['test_users', 'test_accounts', 'test_payees', 'test_tags', 'test_transactions', 'test_taglinks']
    
    def test_tag_suggest(self):
        a = Account.objects.get(pk=3)

        p = Payee.objects.get(name="Sainsbury's")
        tags = p.suggest_tags(a.user)
        self.assertEqual(tags, [u'food', u'household'])
        
        p = Payee.objects.get(name="HMV")
        tags = p.suggest_tags(a.user)
        self.assertEqual(tags, [u'cds', u'entertainment', u'birthdays', u'dvds', u'presents'])
        
        t = Transaction.objects.create(account=a, mobile=False, payee=p, amount=Decimal('-50'), date=datetime.date.today())
        
        # By creating these tags we should move presents up the ranking, and add in books
        TagLink.create_relationships(t, 'books cds presents')
        
        tags = p.suggest_tags(a.user)
        self.assertEqual(tags, [u'cds', u'entertainment', u'birthdays', u'presents', u'dvds', u'books'])
