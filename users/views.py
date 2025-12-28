from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required
def show_my_profile(request):
    return render(request,'user/my_account.html',

    )