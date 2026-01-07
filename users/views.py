import datetime

import plotly.graph_objects as go
import plotly.offline as pyo
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from users.forms import SingUpForm, CompleteProfileForm, CompleteDietaryPreferences, AddWeightLog
from users.models import UserProfile, DietaryPreferences, WeightLog


# Create your views here.
@login_required
def show_my_profile(request: HttpRequest) -> HttpResponse:
    user = request.user

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    latest_weight = user.weight_logs.first()
    if latest_weight is None:
        latest_weight = user.profile.weight

    return render(request, 'user/my_account.html',
                  {
                      'user': user,
                      'profile': profile,
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
            messages.success(request, f'Welcome back, {user.get_username()}.')
            if not hasattr(request.user, 'profile'):
                messages.info(request, 'You need to complete your profile.')
                return redirect('/complete_profile/')
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


def check_date_conditions(form: CompleteProfileForm) -> bool:
    birth_date = form.cleaned_data.get('birth_date')
    goal_date = form.cleaned_data.get('goal_date')
    now = datetime.date.today()
    if birth_date < goal_date and birth_date < now < goal_date:
        return True
    else:
        return False


@login_required
def complete_profile(request: HttpRequest) -> HttpResponse:
    if hasattr(request.user, 'profile'):
        messages.info(request, 'You already have a profile')
        return redirect('/food_logs/')

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST)
        if form.is_valid() and check_date_conditions(form):

            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            messages.success(request, 'User profile data inserted.')
            return redirect('complete_dietary_preferences')

        else:
            messages.error(request, "Error when creating user profile.")

    else:
        form = CompleteProfileForm()

    return render(request, 'user/complete_profile.html', {'form': form})


@login_required
def complete_dietary_preferences(request: HttpRequest) -> HttpResponse:
    try:
        preferences = request.user.dietary_preferences
        messages.info(request, 'You already have a dietary preferences')
        return redirect('food_logs')
    except DietaryPreferences.DoesNotExist:
        pass

    if request.method == 'POST':
        form = CompleteDietaryPreferences(request.POST)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.user = request.user
            preferences.save()

            messages.success(request, 'Dietary preferences inserted.')
            return redirect('food_logs')

        else:
            messages.error(request, "Error when adding dietary preferences.")

    else:
        form = CompleteDietaryPreferences()

    return render(request, 'user/complete_dietary_preferences.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('sign_in')


@login_required
def update_weight_log(request, log_id):
    weight_log=get_object_or_404(WeightLog,id=log_id, user=request.user)
    if request.method == 'POST':
        form=AddWeightLog(request.POST,instance=weight_log)
        if form.is_valid():
            form.save()
            return redirect('show_weight_logs')
    else:
        form=AddWeightLog(instance=weight_log)

    return render(request, 'user/add_weight_log.html', {
        'weight_log': weight_log,
        'form':form,
    })

@login_required
def delete_weight_log(request, log_id):
    weight_log = get_object_or_404(WeightLog, id=log_id, user=request.user)

    if request.method == 'POST':
        weight_log.delete()
        return redirect('show_weight_logs')
    else:
        return redirect('show_weight_logs')

@login_required
def show_weight_logs(request: HttpRequest) -> HttpResponse:
    user = request.user
    weight_logs_for_chart = user.weight_logs.all().order_by('date')
    weight_logs= user.weight_logs.all()
    profile = user.profile

    target_weight = float(profile.target_weight) if profile.target_weight else None
    initial_weight = float(profile.weight) if profile.weight else None

    all_data = (
                   [{'date': profile.created_at.strftime('%d %b'), 'weight': initial_weight}] if initial_weight else []
               ) + list(map(
        lambda log: {'date': log.date.strftime('%d %b'), 'weight': float(log.weight)},
        weight_logs_for_chart
    ))

    dates = [item['date'] for item in all_data]
    weights = [item['weight'] for item in all_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=weights,
        name='Weight',
        marker=dict(
            color='rgb(75, 192, 192)',
            line=dict(color='rgb(50, 150, 150)', width=1.5)
        ),
        text=weights,
        textposition='inside',
        texttemplate='%{text:.1f}',

        hovertemplate='<b>Weight: %{y:.1f} kg<extra></extra>'
    ))

    if target_weight:
        fig.add_trace(go.Scatter(
            x=dates,
            y=[target_weight] * len(dates),
            mode='lines',
            name='Target Weight',
            line=dict(
                color='rgba(255, 206, 86, 0.8)',
                width=3,
                dash='dot'
            ),
            hovertemplate=f'Target: {target_weight:.1f} kg<extra></extra>'
        ))

    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(
            type='category',
            tickmode='linear',
        ),
        yaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.3)',
        ),
        margin=dict(t=50, b=100, l=60, r=30),
        height=450,
        plot_bgcolor='rgba(33, 37, 41, 0.95)',
        paper_bgcolor='rgba(33, 37, 41, 0.95)',
        font=dict(color='white'),
        showlegend=False,
    )

    chart_html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')

    return render(request, 'user/show_weight_logs.html',
                  {
                      'user': user,
                      'weight_logs': weight_logs,
                      'profile': profile,
                      'chart_html': chart_html,
                  })


@login_required
def add_weight_log(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = AddWeightLog(request.POST)
        if form.is_valid():
            weight_log = form.save(commit=False)
            weight_log.user = request.user
            weight_log.save()
            messages.success(request, 'Weight log inserted.')
            return redirect('show_weight_logs')

        else:
            messages.error(request, "Error when adding weight log.")
    else:
        form = AddWeightLog()

    return render(request, 'user/add_weight_log.html', {'form': form})
