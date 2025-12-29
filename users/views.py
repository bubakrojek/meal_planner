from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from users.forms import SingUpForm, CompleteProfileForm
from users.models import UserProfile, DietaryPreferences


# Create your views here.
@login_required
def show_my_profile(request: HttpRequest) -> HttpResponse:
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


def sign_in(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('food_logs')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")

        if form.is_valid():

            user = form.get_user()

            login(request, user)
            messages.success(request,f'Welcome back, {user.get_username()}.')
            return redirect('/food_logs/')
        else:
            messages.info(request, 'Username or password is invalid.')
    else:
        form = AuthenticationForm()

    return render(request, 'user/sign_in.html', context={
        'form': form,
    })


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('food_logs')
    if request.method == 'POST':
        form = SingUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            authenticate(username=username, password=raw_password)
            messages.success(request, 'Account created! Please log in.')
            # login(request,user)
            return redirect('/sign_in/')
    else:
        form = SingUpForm()

    return render(request, 'user/register.html', context={
        'form': form,
    })


@login_required
def complete_profile(request: HttpRequest) -> HttpResponse:
    if hasattr(request.user, 'profile'):
        messages.info(request, 'You already have a profile')
        return redirect('/food_logs/')

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data.get('weight')
            height = form.cleaned_data.get('height')
            birth_date = form.cleaned_data.get('birth_date')
            gender = form.cleaned_data.get('gender')
            activity_level = form.cleaned_data.get('activity_level')
            target_weight = form.cleaned_data.get('target_weight')
            goal_date = form.cleaned_data.get('goal_date')
            user=request.user
            profile=UserProfile.objects.create(
                user=user,
                height=height,
                birth_date=birth_date,
                weight=weight,
                gender=gender,
                activity_level=activity_level,
                target_weight=target_weight,
                goal_date=goal_date,
            )

            messages.success(request, 'User profile data inserted.')
            return redirect('/food_logs/')

        else:
            messages.info(request,"Error when creating user profile.")

    else:
        form=CompleteProfileForm()

    return render(request,'user/complete_profile.html',{'form':form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('/sign_in/')
