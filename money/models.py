from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Count
from django.utils.translation import ugettext as _
import datetime
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save

# Create your models here.
class Tag(models.Model):
    """
    A single tag
    """
    name = models.CharField(max_length=20,db_index=True,unique=True)
    def __unicode__(self):
        return self.name

class Payee(models.Model):
    """
    A payee - these are system-wide rather than user-specific in order to improve usability
    """
    name = models.CharField(max_length=50,db_index=True,unique=True)
    def __unicode__(self):
        return self.name
    
    def suggest_tags(self):
        return Tag.objects.filter(taglink__transaction__payee=self).annotate(count=Count('id', distinct=True)).order_by('count', 'name')

class Bank(models.Model):
    """
    Encapsulates a bank
    Could be used to store details about how to retrieve information from that bank
    """
    name = models.CharField(max_length=50,db_index=True,unique=True)
    def __unicode__(self):
        return self.name
    
class Account(models.Model):
    """
    Encapsulates a bank account
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    number = models.PositiveIntegerField(blank=True,null=True)
    sort_code = models.CharField(max_length=8,blank=True)
    bank = models.ForeignKey(Bank,blank=True,null=True)
    starting_balance = models.DecimalField(decimal_places=2,max_digits=9,default=0.00)
    balance = models.DecimalField(decimal_places=2,max_digits=9,default=0.00)
    balance_updated = models.DateTimeField()
    track_balance = models.BooleanField(help_text=_(u'Turn this off if you want to use a cash account without tracking the balance'), default=True)
    currency = models.CharField(max_length=3)
    date_created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name
    
    def update_balance(self, all=False):
        """
        Updates the balance of the account
        
        Arguments:
        all -- whether to update using all transactions or just since last updated
        """
        # Only update the balance if we're tracking the balance for this account
        if (self.track_balance == True):
            transactions = Transaction.objects.filter(account=self)
            if (all == False):
                transactions = transactions.filter(date_created__gt=self.balance_updated)
                b = self.balance;
            else:
                b = self.starting_balance
            
            transactions = transactions.values('account__id').annotate(Sum('amount'))
                
            if (transactions):
                for t in transactions:
                    b += t['amount__sum']
                
                self.balance = b;
                self.balance_updated = datetime.datetime.now()
                self.save()
        
    def balance_at(self, datetime):
        """ 
        Gets the balance at a particular date and time
        """
        self.update_balance()
        b = self.balance
        transactions = Transaction.objects.filter(account=self,date__gte=datetime).values('account__id').annotate(Sum('amount'))
        
        for t in transactions:
            b -= t.amount__sum
        
        return b
    
    class Meta:
        unique_together = ('user', 'number', 'sort_code', 'bank')

class Transaction(models.Model):
    """
    Encapsulates a transaction
    """
    mobile = models.BooleanField(default=False)
    account = models.ForeignKey(Account)
    payee = models.ForeignKey(Payee)
    amount = models.DecimalField(decimal_places=2,max_digits=8)
    date = models.DateField(db_index=True)
    tags = models.ManyToManyField(Tag, through='TagLink')
    comment = models.TextField(blank=True)
    transfer = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.payee.name + u' (' + unicode(self.amount) + u' on ' + unicode(self.date) + u')'
    
    @staticmethod
    def on_save(**kwargs):
        if 'instance' in kwargs.keys() and 'sender' in kwargs.keys() and kwargs['sender'] is Transaction:
            inst = kwargs['instance']
            # If the model was created, we only need to use the transactions created since the last balance
            # update
            if 'created' in kwargs and kwargs['created']:
                inst.account.update_balance(False)
            # Otherwise, we update the balance using all the transactions in the database
            else:
                inst.account.update_balance(True)
    
    @staticmethod
    def on_delete(**kwargs):
        if 'instance' in kwargs.keys() and 'sender' in kwargs.keys() and kwargs['sender'] is Transaction:
            kwargs['instance'].account.update_balance(True)
    
# Attach listeners for delete and save signals so we can update the account's balance
post_delete.connect(Transaction.on_delete, sender=Transaction)
post_save.connect(Transaction.on_save, sender=Transaction)

class TagLink(models.Model):
    """
    Links a tag with a transaction (many to many) including its split (i.e. how much the tag counts for in this transaction)
    """
    transaction = models.ForeignKey(Transaction)
    tag = models.ForeignKey(Tag)
    split = models.DecimalField(decimal_places=2,max_digits=8)
    def __unicode__(self):
        return self.transaction.payee.name + u' - ' + self.tag.name
    
    class Meta:
        unique_together = ('transaction', 'tag')