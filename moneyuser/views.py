from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from moneyuser.forms import RegisterForm

# Create your views here.
@login_required
def profile(request):
    pass

def register(request):
    dashboard = reverse('moneydj.dashboard.views.index')
    
    if request.user.is_authenticated():
        return redirect(dashboard)
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _('You have been successfully registered. You may now proceed to log in'))
            return redirect(dashboard)
        
    else:
        form = RegisterForm()
        
    return render_to_response('registration/register.html', { 'form': form }, context_instance=RequestContext(request))
