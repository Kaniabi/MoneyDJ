# coding=utf8
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.models import check_password
from moneydj.money.models import Account
from django.core import serializers
from django.contrib.auth.models import User

# Create your views here.
def get_accounts(request):
    """ Gets a JSON object containing the user's accounts """
    if (not request.method == 'POST' or 'username' not in request.POST.keys() or 'password' not in request.POST.keys()) and request.user.is_anonymous():
        return HttpResponseBadRequest()
    
    if not request.user.is_anonymous():
        user = request.user
    else:
        user = get_object_or_404(User, username=request.POST['username'])
    
        if not check_password(request.POST['password'], user.password):
            return HttpResponseForbidden()
    
    return HttpResponse(serializers.serialize('json', Account.objects.filter(user=user), ensure_ascii=False), content_type='application/javascript; charset=utf-8')