from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from domain.food_log import get_certain_food_log, get_day_macros, get_recipes, get_date, sum_day_macros, \
    get_macroelements_percentages
from recipes.forms import FoodLogForm
from django.contrib import messages


# Create your views here.

@login_required
def certain_food_log(request: HttpRequest) -> HttpResponse:
    date_str = request.GET.get('date')

    date=get_date(date_str)
    dates = [date + timedelta(days=i) for i in range(-3, 4)]

    food_logs = get_certain_food_log(user=request.user, date=date)
    day_macros = get_day_macros(user=request.user, date=date)
    summed_day_macroelements=sum_day_macros(user=request.user, date=date)
    percentages=get_macroelements_percentages(actual_macroelements=summed_day_macroelements,user=request.user)

    return render(request, 'food_logs/certain_food_log.html', {
        'user': request.user,
        'food_logs_types': food_logs,
        'day_macros': day_macros,
        'dates': dates,
        'this_date':date,
        'calculated_macroelements':request.user.profile.macronutrients,
        'summed_day_macroelements':summed_day_macroelements,
        'percentages':percentages,
    })

@login_required
def add_food_log(request:HttpRequest,date:str,meal_type:str)->HttpResponse:
    date = datetime.strptime(date, '%Y-%m-%d').date()
    recipes=get_recipes()
    if request.method=='POST':
        form=FoodLogForm(request.POST)
        if form.is_valid():
            food_log=form.save(commit=False)
            food_log.date=date
            food_log.meal_type=meal_type
            food_log.user=request.user
            food_log.save()

            messages.success(request,'Food log created successfully!')
            url=reverse('food_logs')
            return redirect(f'{url}?date={date}')

        else:
            messages.error(request,'Error when adding food log.')
    else:
        form=FoodLogForm()

    return render(request,'food_logs/add_food_log.html',
                  {
                      'form':form,
                      'recipes':recipes,
                  })

