import csv
import codecs
import simplejson

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

file = codecs.open('/Users/rayj/Downloads/Currencies.csv', 'r', 'utf-8')
# file = open('/Users/rayj/Downloads/Currencies.csv', 'r')

# f = csv.reader(file)
f = unicode_csv_reader(file)
a = u""

pk = 1
for r in f:
	a += u"INSERT INTO `money_currency` (`code`, `symbol`, `country`, `name`) VALUES "
	country_name = r[0].rsplit(',',1)
	if len(country_name) is 2:
		country = country_name[0].strip()
		name = country_name[1].strip()
	else:
		country = u''
		name = country_name[0].strip()
	a += u"('" + r[1] + u"', '" + r[2] + u"', '" + country + u"', '" + name + u"');\n"
	pk += 1

fw = codecs.open('currency.sql', 'w', 'utf-8')

fw.write(a)

file.close()
fw.close()
