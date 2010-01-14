# Based on the code at http://code.google.com/p/python-money/
from decimal import Decimal

class Currency:
    code = u""
    country = u""
    countries = []
    name = u""
    numeric = u""
    exchange_rate = Decimal(1.0)
    def __init__(self, code=u"", numeric=u"", name=u"", countries=[]):
        self.code = code
        self.numeric = numeric
        self.name = name
        self.countries = countries
    def __repr__(self):
        return self.code
    def __unicode__(self):
        return unicode(self.__repr__())
    def set_exchange_rate(self, rate):
        if not isinstance(rate, Decimal):
            rate = Decimal(str(rate))
        self.exchange_rate = rate