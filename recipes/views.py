from datetime import datetime, timedelta, date
from typing import Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from domain.food_log import get_certain_food_log, get_day_macros, get_recipes, get_date, sum_day_macros, \
    get_macroelements_percentages, create_recipe_from_food_log
from domain.meal_planning import get_weekly_plan, get_meal_types, save_weekly_plan_to_db, \
    get_existing_meal_types, generate_daily_meal_plan, save_daily_plan_to_db, copy_plan_to_food_logs, \
    generate_weekly_meal_plan_optimized
from domain.recipe_api import search_recipes_api
from recipes.forms import FoodLogForm
from recipes.models import FoodLog, PlannedMeal


# Create your views here.


@login_required
def certain_food_log(request: HttpRequest) -> HttpResponse:
    date_str = request.GET.get('date')

    date = get_date(date_str)
    dates = [date + timedelta(days=i) for i in range(-3, 4)]

    food_logs = get_certain_food_log(user=request.user, date=date)
    day_macros = get_day_macros(user=request.user, date=date)
    summed_day_macroelements = sum_day_macros(user=request.user, date=date)
    percentages = get_macroelements_percentages(actual_macroelements=summed_day_macroelements, user=request.user)

    return render(request, 'food_logs/certain_food_log.html', {
        'user': request.user,
        'food_logs_types': food_logs,
        'day_macros': day_macros,
        'dates': dates,
        'this_date': date,
        'calculated_macroelements': request.user.profile.macronutrients,
        'summed_day_macroelements': summed_day_macroelements,
        'percentages': percentages,
    })


def create_food_log_from_database(user: User, post_data: Dict) -> FoodLog:
    return FoodLog(
        user=user,
        date=post_data.get('date'),
        meal_type=post_data.get('meal_type'),
        recipe_id=post_data.get('recipe'),
        servings=int(post_data.get('servings', 1))

    )


def create_food_log_from_api(user: User, post_data: Dict) -> FoodLog:
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
def add_food_log(request: HttpRequest, date: str, meal_type: str) -> HttpResponse:
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    recipes = get_recipes()
    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            recipe_source = request.POST.get('recipe_source')
            creators = {
                'database': create_food_log_from_database,
                'api': create_food_log_from_api,
                'custom': create_food_log_custom
            }

            creator = creators.get(recipe_source, create_food_log_from_database)

            post_data_with_params = {
                **request.POST.dict(),
                'date': date_obj,
                'meal_type': meal_type
            }

            food_log = creator(request.user, post_data_with_params)

            if recipe_source == 'custom':
                create_recipe_from_food_log(
                    title=food_log.custom_title,
                    calories=float(food_log.custom_calories),
                    protein=float(food_log.custom_protein),
                    carbohydrates=float(food_log.custom_carbohydrates),
                    fat=float(food_log.custom_fat),
                    servings=food_log.servings,
                    user=request.user,
                )
            food_log.save()

            messages.success(request, 'Food log created successfully!')
            url = reverse('food_logs')
            return redirect(f'{url}?date={date}')

        else:
            messages.error(request, 'Error when adding food log.')
    else:
        form = FoodLogForm()

    return render(request, 'food_logs/add_food_log.html',
                  {
                      'form': form,
                      'recipes': recipes,
                  })


@login_required
def update_food_log(request: HttpRequest, log_id) -> HttpResponse:
    food_log = get_object_or_404(FoodLog, id=log_id, user=request.user)
    date = food_log.date
    if request.method == 'POST':
        form = FoodLogForm(request.POST, instance=food_log)
        if form.is_valid():
            form.save()
            url = reverse('food_logs')
            return redirect(f'{url}?date={date}')
    else:
        form = FoodLogForm(instance=food_log)

    return render(request, 'food_logs/add_food_log.html', {
        'food_log': food_log,
        'form': form,
    })


@login_required
def delete_food_log(request: HttpRequest, log_id) -> HttpResponse:
    food_log = get_object_or_404(FoodLog, id=log_id, user=request.user)
    date = food_log.date
    if request.method == 'POST':
        food_log.delete()
        url = reverse('food_logs')
        return redirect(f'{url}?date={date}')
    else:
        url = reverse('food_logs')
        return redirect(f'{url}?date={date}')


@login_required
def search_recipes_htmx(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')

    if len(query) < 3:
        return render(request, 'food_logs/api_results.html', {'recipes': []})

    recipes = search_recipes_api(
        query=query,
        api_key=settings.SPOONACULAR_API_KEY,
        number=5
    )

    return render(request, 'food_logs/api_results.html', {'recipes': recipes})


@login_required
def generate_meal_plan(request: HttpRequest) -> HttpResponse:
    user_profile = request.user.profile
    preferences = request.user.dietary_preferences

    if request.method == "POST":
        start_date_str = request.POST.get('start_date')
        start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()

        meal_types = request.POST.getlist('meal_types')
        if not meal_types:
            meal_types = get_meal_types()

        target_macros = user_profile.macronutrients

        weekly_plan = generate_weekly_meal_plan_optimized(
            start_date,
            target_macros,
            preferences,
            settings.SPOONACULAR_API_KEY,
            meal_types
        )

        saved_count = save_weekly_plan_to_db(request.user, weekly_plan)

        messages.success(request, f'Generated and saved {saved_count} meals for the week!')
        return redirect(f'/meal_plan/?week_start={start_date.isoformat()}')

    return render(request, 'meal_planning/generate.html', {
        'user_macros': user_profile.macronutrients,
        'preferences': preferences,
        'today': date.today(),
    })


@login_required
def regenerate_day(request: HttpRequest, date_str: str) -> HttpResponse:
    target_date = date.fromisoformat(date_str)

    user_profile = request.user.profile
    preferences = request.user.dietary_preferences

    existing_meal_types = get_existing_meal_types(request.user, target_date)
    daily_plan = generate_daily_meal_plan(
        target_macros=user_profile.macronutrients,
        preferences=preferences,
        api_key=settings.SPOONACULAR_API_KEY,
        meal_types=existing_meal_types or ['breakfast', 'lunch', 'dinner']
    )

    save_daily_plan_to_db(request.user, daily_plan, target_date)

    messages.success(request, f'Regenerated all meals for {target_date}!')
    return redirect(f'/meal_plan/?week_start={target_date.isoformat()}')


@login_required
def weekly_meal_plan_view(request: HttpRequest) -> HttpResponse:
    week_start = request.GET.get('week_start')
    if week_start:
        start_date = date.fromisoformat(week_start)
    else:
        start_date = date.today()

    weekly_plan = get_weekly_plan(request.user, start_date)

    prev_week = start_date - timedelta(days=7)
    next_week = start_date + timedelta(days=7)

    return render(request, 'meal_planning/calendar.html', {
        'weekly_plan': weekly_plan,
        'start_date': start_date,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': date.today()
    })


@login_required
def execute_daily_plan(request, date_str: str) -> HttpResponse:
    target_date = date.fromisoformat(date_str)

    count = copy_plan_to_food_logs(request.user, target_date)

    if count > 0:
        messages.success(
            request,
            f'Successfully copied {count} meal(s) to your food log for {target_date.strftime("%B %d, %Y")}!'
        )
    else:
        messages.warning(
            request,
            f'No meals found in the plan for {target_date.strftime("%B %d, %Y")}.'
        )

    return redirect(f'/food_logs/?date={date_str}')


@login_required
def delete_planned_meal(request, meal_id: int):
    try:
        meal = PlannedMeal.objects.get(id=meal_id, user=request.user)
        meal_date = meal.date
        meal.delete()
        messages.success(request, f'Deleted meal from plan!')
    except PlannedMeal.DoesNotExist:
        messages.error(request, 'Meal not found.')
        meal_date = date.today()

    return redirect(f'/meal_plan/?week_start={meal_date.isoformat()}')
