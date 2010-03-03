from django import template

register = template.Library()

@register.inclusion_tag('tag_cloud.html')
def cloud(items, credit=None):
    cloud = []
    max = 0
    min = 0
    
    # Figure out the max and min values
    for i in items:
        if i['total'] > max:
            max = i['total']
        if i['total'] < min or min == 0:
            min = i['total']
            
    if not credit:
        max, min = min, max
            
    diff = max - min
    
    for i in items:
        percent = (i['total'] - min) / diff
        cloud.append({'name': i['tag__name'],
                      # Distribute the cloud over 10 levels of granularity
                      'val': int(round(percent * 9) + 1),
                      'amount': unicode(str(i['total']))})
        
    return {'cloud': cloud}