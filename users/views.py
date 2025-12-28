from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

from users.forms import SingUpForm
from users.models import UserProfile, DietaryPreferences


# Create your views here.
@login_required
def show_my_profile(request):
    user = request.user

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    try:
        preferences = user.dietary_preferences
    except DietaryPreferences.DoesNotExist:
        preferences = None

    latest_weight = user.weight_logs.first()

    return render(request, 'user/my_account.html',
                  {
                      'user': user,
                      'profile': profile,
                      'preferences': preferences,
                      'latest_weight': latest_weight
                  }

                  )


def sign_up(request):

    if request.method=='POST':
        sign_up_form=SingUpForm(request.POST)
        if sign_up_form.is_valid():
            user=sign_up_form.save()
            user.refresh_from_db()

            username=sign_up_form.cleaned_data.get('username')
            raw_password=sign_up_form.cleaned_data.get('password1')
            user=authenticate(username=username,password=raw_password)
            login(request,user)


    else:
        sign_up_form=SingUpForm()

        return render(request,'user/sign_up.html',context={
            'form':sign_up_form,
        })
