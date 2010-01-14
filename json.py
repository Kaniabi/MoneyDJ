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

f.next()
a = []

pk = 1
for r in f:
	country_name = r[0].rsplit(',',1)
	if len(country_name) is 2:
		country = country_name[0].strip()
		name = country_name[1].strip()
	else:
		country = ''
		name = country_name[0].strip()
	a.append({u'model': u'money.Currency', u'fields': {u'code': r[1], u'symbol': r[2], u'country': country, u'name': name}, u'pk': pk})
	pk += 1

print a[2]['fields']['symbol']
fw = codecs.open('initial_data.json', 'w', 'utf-8')

fw.write(simplejson.dumps(a, indent=4, ensure_ascii=False))
# print simplejson.dumps(a, indent=4, ensure_ascii=False)

file.close()
fw.close()

# fw = open('initial_data.json', 'r')
fw = codecs.open('initial_data.json', 'r', 'utf-8')

json = simplejson.load(fw)

fw.close()

print json
