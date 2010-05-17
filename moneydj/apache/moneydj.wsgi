#!/bin/python
import os
import sys
sys.path.append('/home/joe/Sites/MoneyDJ/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'moneydj.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
