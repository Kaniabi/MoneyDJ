from django.db import models
from moneydj.accounts import Transaction

# Create your models here.
class Tag(models.Model):
    """
    A single tag
    """
    name = models.CharField(max_length=20,db_index=True,unique=True)
    def __unicode__(self):
        return self.name
    
class TagLink(models.Model):
    """
    Links a tag with a transaction (many to many) including its split
    """
    transaction = models.ForeignKey(Transaction)
    tag = models.ForeignKey(Tag)
    split = models.IntegerField(default=100)
    def __unicode__(self):
        return self.transaction.payee.name + u' - ' + self.tag.name
    
    class Meta:
        unique_together = ('transaction', 'tag')