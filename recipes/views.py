from datetime import datetime, timedelta
from typing import Dict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from domain.food_log import get_certain_food_log, get_day_macros, get_recipes, get_date, sum_day_macros, \
    get_macroelements_percentages, create_recipe_from_food_log
from domain.recipe_api import search_recipes_api
from recipes.forms import FoodLogForm
from django.contrib import messages

from recipes.models import FoodLog


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

def create_food_log_from_database(user:User, post_data:Dict)->FoodLog:
    return FoodLog(
        user=user,
        date=post_data.get('date'),
        meal_type=post_data.get('meal_type'),
        recipe_id=post_data.get('recipe'),
        servings=int(post_data.get('servings',1))

    )

def create_food_log_from_api(user:User, post_data:Dict)->FoodLog:
    return FoodLog(
        user=user,
        date=post_data.get('date'),
        meal_type=post_data.get('meal_type'),
        recipe=None,
        custom_title=post_data.get('api_recipe_title'),
        custom_calories=float(post_data.get('api_recipe_calories', 0)),
        custom_protein=float(post_data.get('api_recipe_protein', 0)),
        custom_carbohydrates=float(post_data.get('api_recipe_carbohydrates', 0)),
        custom_fat=float(post_data.get('api_recipe_fat', 0)),
        servings=int(post_data.get('servings', 1))
    )

def create_food_log_custom(user, post_data: Dict) -> FoodLog:
     return FoodLog(
        user=user,
        date=post_data.get('date'),
        meal_type=post_data.get('meal_type'),
        recipe=None,
        custom_title=post_data.get('custom_title'),
        custom_calories=float(post_data.get('custom_calories', 0)),
        custom_protein=float(post_data.get('custom_protein', 0)),
        custom_carbohydrates=float(post_data.get('custom_carbohydrates', 0)),
        custom_fat=float(post_data.get('custom_fat', 0)),
        servings=int(post_data.get('servings', 1))
    )

@login_required
def add_food_log(request:HttpRequest,date:str,meal_type:str)->HttpResponse:
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    recipes=get_recipes()
    if request.method=='POST':
        form=FoodLogForm(request.POST)
        if form.is_valid():
            recipe_source = request.POST.get('recipe_source')
            creators = {
                'database': create_food_log_from_database,
                'api': create_food_log_from_api,
                'custom': create_food_log_custom
            }

            creator=creators.get(recipe_source,create_food_log_from_database)

            post_data_with_params = {
                **request.POST.dict(),
                'date': date_obj,
                'meal_type': meal_type
            }

            food_log=creator(request.user,post_data_with_params)

            if recipe_source=='custom':
                create_recipe_from_food_log(
                    title=food_log.custom_title,
                    calories=food_log.custom_calories,
                    protein=food_log.custom_protein,
                    carbohydrates=food_log.custom_carbohydrates,
                    fat=food_log.custom_fat,
                    servings=food_log.servings,
                    user=request.user,
                )
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

@login_required
def update_food_log(request, log_id):
    food_log=get_object_or_404(FoodLog,id=log_id, user=request.user)
    date = food_log.date
    if request.method == 'POST':
        form=FoodLogForm(request.POST,instance=food_log)
        if form.is_valid():
            form.save()
            url = reverse('food_logs')
            return redirect(f'{url}?date={date}')
    else:
        form=FoodLogForm(instance=food_log)

    return render(request, 'food_logs/add_food_log.html', {
        'food_log': food_log,
        'form':form,
    })

@login_required
def delete_food_log(request, log_id):
    food_log = get_object_or_404(FoodLog, id=log_id, user=request.user)
    date=food_log.date
    if request.method == 'POST':
        food_log.delete()
        url = reverse('food_logs')
        return redirect(f'{url}?date={date}')
    else:
        url = reverse('food_logs')
        return redirect(f'{url}?date={date}')


def search_recipes_htmx(request):
    query=request.GET.get('q','')

    if len(query)<3:
        return render(request,'food_logs/api_results.html',{'recipes':[]})

    recipes= search_recipes_api(
        query=query,
        api_key=settings.SPOONACULAR_API_KEY,
        number=5
    )

    return render(request,'food_logs/api_results.html',{'recipes':recipes})