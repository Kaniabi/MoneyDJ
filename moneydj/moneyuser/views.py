from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login
from moneydj.moneyuser.forms import RegisterForm

# Create your views here.
@login_required
def profile(request):
    pass

def register(request):
    if request.user.is_authenticated():
        return redirect(reverse('moneydj.dashboard.views.index'))
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            u = form.save()
            u = authenticate(username=u.username, password=form.cleaned_data['password1'])
            if u is not None:
                login(request, u)
                messages.add_message(request, messages.SUCCESS, _('Thank you for registering, %s. You are now logged in.' % u.username))
                return redirect(reverse('dashboard'))

            messages.add_message(request, messages.SUCCESS, _('Thank you for registering, %s. You may now proceed to log in.' % u.username))
            return redirect(reverse('django.contrib.auth.views.login'))
        
    else:
        form = RegisterForm()
        
    return render_to_response('registration/register.html', { 'form': form }, context_instance=RequestContext(request))
