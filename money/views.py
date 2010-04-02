from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('moneydj.dashboard.views.index'))
    else:
        return redirect(reverse('django.contrib.auth.views.logout_then_login'))