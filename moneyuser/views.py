
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def profile(request):
    pass