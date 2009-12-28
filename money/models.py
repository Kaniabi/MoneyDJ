from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return self.name

class Payee(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Bank(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    
class Account(models.Model):
    name = models.CharField(max_length=50)
    number = models.IntegerField(blank=True)
    sort_code = models.CharField(max_length=8)
    bank = models.ForeignKey(Bank)
    def __unicode__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User)
    check_no = models.PositiveIntegerField(null=True,blank=True,db_index=True)
    payee = models.ForeignKey(Payee)
    amount = models.DecimalField(decimal_places=2,max_digits=8)
    credit = models.BooleanField(default=False)
    date = models.DateField(db_index=True)
    tags = models.ManyToManyField(Tag, through='TagLink')
    def __unicode__(self):
        return self.payee.name + u' (' + unicode(self.amount) + u' on ' + unicode(self.date) + u')'

class TagLink(models.Model):
    transaction = models.ForeignKey(Transaction)
    tag = models.ForeignKey(Tag)
    split = models.IntegerField(default=100)
    def __unicode__(self):
        return self.transaction.payee.name + u' - ' + self.tag.name