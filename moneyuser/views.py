from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext

# Create your views here.
@login_required
def profile(request):
    pass

def register(request):
    dashboard = reverse('moneydj.dashboard.views.index')
    
    if request.user.is_authenticated():
        return redirect(dashboard)
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(dashboard)
        
    else:
        form = UserCreationForm()
        
    return render_to_response('registration/register.html', { 'form': form }, context_instance=RequestContext(request))