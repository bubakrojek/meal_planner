import time
from datetime import date, timedelta
from functools import reduce
from typing import List, Dict, Optional, Any

import requests
from django.contrib.auth.models import User
from django.db.models import QuerySet

from domain.recipe_api import extract_nutrient_amount, extract_ingredients, aggregate_ingredients
from recipes.models import PlannedMeal, FoodLog
from users.models import DietaryPreferences


def get_meal_portions() -> Dict[str, float]:
    return {
        'breakfast': 0.25,
        'lunch': 0.35,
        'dinner': 0.30,
        'supper': 0.05,
        'snack': 0.05,
    }


def calculate_meal_target_macros(daily_macros: Dict, meal_type: str) -> Dict[str, float]:
    portions = get_meal_portions()
    portion = portions.get(meal_type, 0.25)

    return {
        'calories': daily_macros['calories'] * portion,
        'protein': daily_macros['protein'] * portion,
        'carbohydrates': daily_macros['carbohydrates'] * portion,
        'fat': daily_macros['fat'] * portion,
    }


def map_preferences_to_api_diet(preferences: DietaryPreferences) -> Optional[str]:
    if preferences is None:
        return None
    if preferences.is_vegan:
        return 'vegan'
    elif preferences.is_vegetarian:
        return 'vegetarian'
    elif preferences.is_gluten_free:
        return 'gluten free'
    elif preferences.is_keto:
        return 'ketogenic'
    elif preferences.is_dairy_free:
        return 'dairy free'
    return None


def map_meal_type_to_api(meal_type: str) -> str:
    mapping = {
        'breakfast': 'breakfast',
        'lunch': 'main course',
        'dinner': 'main course',
        'supper': 'appetizer',
        'snack': 'snack',
    }
    return mapping.get(meal_type, 'main course')


def extract_recipe_from_api_response(api_recipe: Dict) -> Dict:
    return {
        'api_id': api_recipe.get('id'),
        'title': api_recipe.get('title'),
        'image': api_recipe.get('image'),
        'calories': extract_nutrient_amount(api_recipe, 'Calories'),
        'protein': extract_nutrient_amount(api_recipe, 'Protein'),
        'carbohydrates': extract_nutrient_amount(api_recipe, 'Carbohydrates'),
        'fat': extract_nutrient_amount(api_recipe, 'Fat'),
        'servings': api_recipe.get('servings', 1),
        'ingredients': extract_ingredients(api_recipe)
    }


def search_recipe_for_meal(
        meal_type: str,
        target_macros: Dict,
        preferences: DietaryPreferences,
        api_key: str,
        number: int = 1
) -> List[Dict]:
    url = "https://api.spoonacular.com/recipes/complexSearch"
    meal_target = calculate_meal_target_macros(target_macros, meal_type)

    params = {
        'apiKey': api_key,
        'number': number,
        'addRecipeNutrition': True,
        'type': map_meal_type_to_api(meal_type),
        'maxCalories': int(meal_target['calories'] * 1.5),
        'minCalories': int(meal_target['calories'] * 0.5),
        ''''maxProtein': int(meal_target['protein'] * 1.3),
        'minProtein': int(meal_target['protein'] * 0.7),
        'maxCarbs': int(meal_target['carbohydrates'] * 1.3),
        'maxFat': int(meal_target['fat'] * 1.3),'''
        'sort': 'random',
    }

    diet = map_preferences_to_api_diet(preferences)
    if diet:
        params['diet'] = diet

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])

        return list(map(extract_recipe_from_api_response, results))


    except requests.RequestException:
        return []


def generate_daily_meal_plan(
        target_macros: Dict,
        preferences,
        api_key: str,
        meal_types: List[str] = None,
) -> Dict[str, Dict]:
    if meal_types is None:
        meal_types = ['breakfast', 'lunch', 'dinner']

    meals_with_recipes = list(map(
        lambda meal_type: (
            meal_type,
            search_recipe_for_meal(
                meal_type,
                target_macros,
                preferences,
                api_key,
                1
            )
        ),
        meal_types
    ))
    return {
        meal_type: recipes[0]
        for meal_type, recipes in meals_with_recipes
        if recipes
    }


def generate_weekly_meal_plan(
        start_date: date,
        target_macros: Dict,
        preferences,
        api_key: str,
        meal_types: List[str] = None,
) -> List[Dict]:
    return list(map(
        lambda day_offset: {
            'date': start_date + timedelta(day_offset),
            'meals': generate_daily_meal_plan(
                target_macros,
                preferences,
                api_key,
                meal_types
            )
        },
        range(7)
    ))


def generate_weekly_meal_plan_optimized(
        start_date: date,
        target_macros: Dict,
        preferences,
        api_key: str,
        meal_types: List[str] = None,
) -> List[Dict]:
    if meal_types is None:
        meal_types = ['breakfast', 'lunch', 'dinner']

    recipes_by_type = {}

    for meal_type in meal_types:
        time.sleep(1.1)
        recipes = search_recipe_for_meal(
            meal_type,
            target_macros,
            preferences,
            api_key,
            number=7
        )

        # recipes_by_type[meal_type] = recipes

        recipes_by_type[meal_type] = recipes

    return list(map(
        lambda day_offset: {
            'date': start_date + timedelta(days=day_offset),
            'meals': {
                meal_type: recipes_by_type[meal_type][day_offset]
                for meal_type in meal_types
                if day_offset < len(recipes_by_type.get(meal_type, []))
            }
        },
        range(7)
    ))


def save_daily_plan_to_db(user: User, daily_plan: Dict, target_date: date):
    planned_meals = list(map(
        lambda item: PlannedMeal(
            user=user,
            date=target_date,
            meal_type=item[0],
            recipe=None,
            custom_title=item[1]['title'],
            custom_calories=item[1]['calories'],
            custom_protein=item[1]['protein'],
            custom_carbohydrates=item[1]['carbohydrates'],
            custom_fat=item[1]['fat'],
            ingredients_snapshot=item[1]['ingredients'],
            servings=1,
        ),
        daily_plan.items()
    ))

    PlannedMeal.objects.bulk_create(
        planned_meals,
        update_conflicts=True,
        unique_fields=['user', 'date', 'meal_type'],
        update_fields=['custom_title', 'custom_calories', 'custom_protein',
                       'custom_carbohydrates', 'custom_fat', 'servings']
    )

    return len(planned_meals)


def save_weekly_plan_to_db(user, weekly_plan: List[Dict]):
    total_saved = sum(map(
        lambda day: save_daily_plan_to_db(
            user,
            daily_plan=day['meals'],
            target_date=day['date']
        ),
        weekly_plan
    ))

    return total_saved


def sum_daily_macros(meals: List[PlannedMeal]) -> Dict[str, float]:
    return reduce(
        lambda acc, meal: {
            'calories': acc['calories'] + (meal.custom_calories or 0),
            'protein': acc['protein'] + (meal.custom_protein or 0),
            'carbohydrates': acc['carbohydrates'] + (meal.custom_carbohydrates or 0),
            'fat': acc['fat'] + (meal.custom_fat or 0),
        },
        meals,
        {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fat': 0}
    )


###############################################
def generate_date_range(start_date: date, days: int) -> List[date]:
    return [start_date + timedelta(days=i) for i in range(days)]


def get_existing_meal_types(user: User, target_date: date) -> List:
    return list(
        PlannedMeal.objects.filter(
            user=user,
            date=target_date
        ).values_list('meal_type', flat=True)
    )


def get_meal_types() -> List[str]:
    return ['breakfast', 'dinner', 'supper']
    # return ['breakfast', 'lunch', 'dinner', 'supper', 'snack']


def group_by_date(planned_meals: List[PlannedMeal]) -> Dict[date, List]:
    return reduce(
        lambda acc, meal: {
            **acc,
            meal.date: acc.get(meal.date, []) + [meal]
        },
        planned_meals,
        {}
    )


def group_by_type(planned_meals: List[PlannedMeal]) -> Dict[str, List]:
    return reduce(
        lambda acc, meal: {
            **acc,
            meal.meal_type: acc.get(meal.meal_type, []) + [meal]
        },
        planned_meals,
        {}
    )


def get_weekly_plan(user: User, start_date: date) -> List:
    end_date = start_date + timedelta(days=7)

    planned_meals = PlannedMeal.objects.filter(
        user=user,
        date__gte=start_date,
        date__lt=end_date
    ).select_related('recipe')

    grouped = group_by_date(planned_meals)

    return list(map(
        lambda day_offset: {
            'date': start_date + timedelta(days=day_offset),
            'meals': grouped.get(start_date + timedelta(days=day_offset), []),
            'meals_by_type': group_by_type(grouped.get(start_date + timedelta(days=day_offset), []), ),
            'total_macros': sum_daily_macros(
                grouped.get(start_date + timedelta(days=day_offset), [])
            )
        },
        range(7)
    ))


def copy_plan_to_food_logs(user, source_date: date):
    planned_meals = PlannedMeal.objects.filter(
        user=user,
        date=source_date
    )

    results = list(map(
        lambda pm: FoodLog.objects.update_or_create(
            user=user,
            date=pm.date,
            meal_type=pm.meal_type,
            defaults={
                'recipe': pm.recipe,
                'custom_title': pm.custom_title,
                'custom_calories': pm.custom_calories,
                'custom_protein': pm.custom_protein,
                'custom_carbohydrates': pm.custom_carbohydrates,
                'custom_fat': pm.custom_fat,
                'servings': pm.servings,
            }
        ),
        planned_meals
    ))

    return len(results)


def get_ingredients_from_planned_meals(user: User, start_date: date, end_date: date) -> list[dict]:
    snapshots = PlannedMeal.objects.filter(user=user, date__gte=start_date, date__lt=end_date).order_by('date',
                                                                                                        'meal_type').values_list(
        'ingredients_snapshot', flat=True)
    return [snapshot for snapshot in snapshots if snapshot]

def generate_shopping_list(user: User, start_date: date, end_date: date) -> Dict:
    all_ingredients = get_ingredients_from_planned_meals(user, start_date, end_date)
    aggregated = aggregate_ingredients(all_ingredients)
    return dict(sorted(aggregated.items(), key=lambda x: x[1]['name']))