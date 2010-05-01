from decimal import InvalidOperation, Decimal
from django.contrib.auth.models import User
from django.core import serializers
from django.core.cache import cache
from django.db import models
from django.db.models import Sum
from django.db.models.aggregates import Count
from django.db.models.signals import post_delete, post_save
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _
import datetime, re
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

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
    
    def suggest_tags(self, user):
        return [t['name'] for t in Tag.objects.filter(taglink__transaction__payee=self, transaction__account__user=user).values('id', 'name').annotate(count=Count('id')).order_by('-count', 'name')[:10]]

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
    
    def set_balance(self, balance):
        """
        Allows the user to set the current balance, working out the original balance based on the transactions in the database
        """
        if not isinstance(balance, Decimal):
            if type(balance) is 'str' or type(balance) is 'unicode':
                balance = Decimal(balance)
            elif type(balance) is 'float':
                balance = Decimal('%.2f' % balance)
            else:
                balance = Decimal('%.2f' % float(balance))
        
        b = 0
        transactions = Transaction.objects.filter(account=self).values('account__id').annotate(Sum('amount'))
        
        for t in transactions:
            b += t['amount__sum']
            
        self.starting_balance = balance - b
        self.balance = balance
        self.balance_updated = datetime.datetime.now()
    
    @staticmethod
    def get_for_user(user):
        return Account.objects.filter(user=user).order_by('name')
    
    @staticmethod
    def invalidate_cache(**kwargs):
        if 'instance' in kwargs.keys() and 'sender' in kwargs.keys() and kwargs['sender'] is Account:
            key = 'template.cache.accounts_block.%s' % (md5_constructor(urlquote(kwargs['instance'].user.username)).hexdigest(),)
            cache.delete(key)   
    
    class Meta:
        unique_together = ('user', 'number', 'sort_code', 'bank')

post_delete.connect(Account.invalidate_cache, sender=Account)
post_save.connect(Account.invalidate_cache, sender=Account)

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
    
    @staticmethod
    def listen_on():
        """
        Turns the signal listening on
        """
        post_delete.connect(Transaction.on_delete, sender=Transaction)
        post_save.connect(Transaction.on_save, sender=Transaction)
    
    @staticmethod
    def listen_off():
        """
        Turns signal listening off so account balances are not updated. This
        should be done when lots of transactions will be saved/deleted in a 
        short space of time to avoid problems when updating account balances
        """
        post_delete.disconnect(Transaction.on_delete, sender=Transaction)
        post_save.disconnect(Transaction.on_save, sender=Transaction)
    
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
Transaction.listen_on()

class TagLink(models.Model):
    """
    Links a tag with a transaction (many to many) including its split (i.e. how much the tag counts for in this transaction)
    """
    transaction = models.ForeignKey(Transaction)
    tag = models.ForeignKey(Tag)
    split = models.DecimalField(decimal_places=2,max_digits=8)
    
    @staticmethod
    def create_relationships(transaction, tag_string):
        abs_amount = abs(Decimal(transaction.amount))

        used_tags = []

	tag_string = re.sub(':[ \t\n\r]+([0-9]+)', ':\\1', tag_string)
        
        for t in tag_string.split(u' '):
            # partition the tag on the last ':' to get any possible split
            name, delim, split = t.rpartition(u':')
            
            if not name and not split:
                continue
            elif not name:
                # We only have a name, but it's put into the split variable because we're partitioning from the right
                name = split
                split = None
                
            # Strip out whitespace from either end and normalise the name
            name = re.sub('[^A-Za-z0-9_&\-.]', '', name.strip(u' \t\n\r'))
            
            # If we don't have a tag, continue
            if not name:
                continue

            if split:
                try:
                    split = abs(Decimal('%.2f' % float(split)))
                    # Use the total amount if the split is invalid
                    if split > abs_amount or split < 0:
                        split = abs_amount
                except (InvalidOperation, TypeError):
                    # The split couldn't be determined
                    split = abs_amount
            else:
                # A split wasn't specified, so we use the total amount
                split = abs_amount
                
            # Make sure we have the right sign!
            if float(transaction.amount) < 0:
                split = -abs(split)

            # If name is in the used_tags array, we've already tagged this transaction with that tag
            if name in used_tags:
                continue
            else:
                try:
                    tag = Tag(name=name)
                    tag.save()
                    used_tags.append(name)
                except IntegrityError:
                    tag = Tag.objects.filter(name__iexact=name)[0]
                    used_tags.append(name)

            rel = TagLink(tag=tag, transaction=transaction, split=split)
            rel.save()
    
    def __unicode__(self):
        return self.transaction.payee.name + u' - ' + self.tag.name
    
    class Meta:
        unique_together = ('transaction', 'tag')
