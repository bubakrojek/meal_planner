from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect

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


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('food_logs')
    if request.method=='POST':
        sign_in_form=AuthenticationForm(request,data=request.POST)
        if not sign_in_form.is_valid():
            print(f"Form errors: {sign_in_form.errors}")

        if sign_in_form.is_valid():

            user=sign_in_form.get_user()

            login(request,user)
            #messages.success(request,f'Welcome back, {user.get_username()}.')
            return redirect('/food_logs/')
        else:
            messages.info(request,'Username or password is invalid.')
    else:
        sign_in_form=AuthenticationForm()

    return render(request,'user/sign_in.html',context={
        'form':sign_in_form,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('food_logs')
    if request.method=='POST':
        sign_up_form=SingUpForm(request.POST)
        if sign_up_form.is_valid():
            user=sign_up_form.save()
            user.refresh_from_db()

            username=sign_up_form.cleaned_data.get('username')
            raw_password=sign_up_form.cleaned_data.get('password1')
            authenticate(username=username,password=raw_password)
            messages.success(request, 'Account created! Please log in.')
            #login(request,user)
            return redirect('/sign_in/')
    else:
        sign_up_form=SingUpForm()

    return render(request,'user/register.html',context={
        'form':sign_up_form,
    })

def logout_view(request):
    logout(request)
    return redirect('/sign_in/')