from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('moneydj.dashboard.views.index'))
    
    return render_to_response("index.html", context_instance=RequestContext(request))