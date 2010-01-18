from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.translation import ugettext as _

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
                
            if (transactions):
                for t in transactions:
                    if t.credit:
                        b += t.amount
                    else:
                        b -= t.amount
                
                self.balance = b;
                self.balance_updated = datetime.datetime.now()
                self.save()
        
    def balance_at(self, datetime):
        """ 
        Gets the balance at a particular date and time
        """
        self.update_balance()
        b = self.balance
        transactions = Transactions.objects.filter(account=self,date__gte=datetime)
        
        for t in transactions:
            if t.credit:
                b -= t.amount
            else:
                b += t.amount
        
        return b
    
    class Meta:
        unique_together = ('user', 'number', 'sort_code', 'bank')

class Transaction(models.Model):
    """
    Encapsulates a transaction
    """
    mobile = models.BooleanField(default=False)
    account = models.ForeignKey(Account)
    cheque_no = models.PositiveIntegerField(blank=True,db_index=True,null=True)
    payee = models.ForeignKey(Payee)
    amount = models.DecimalField(decimal_places=2,max_digits=8)
    credit = models.BooleanField(default=False)
    date = models.DateField(db_index=True)
    tags = models.ManyToManyField(Tag, through='TagLink')
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField()
    def __unicode__(self):
        return self.payee.name + u' (' + unicode(self.amount) + u' on ' + unicode(self.date) + u')'
    
    class Meta:
        unique_together = ('account', 'cheque_no')

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