from django.contrib.auth.models import User

from recipes.models import Recipe, FoodLog

def val(custom,original):
    return custom if custom is not None else original


def get_entry_macros(food_log: FoodLog) -> dict:
    if food_log.recipe is None and food_log.custom_title is None and food_log.custom_fat is None and food_log.custom_calories is None and food_log.custom_protein is None and food_log.custom_carbohydrates:
        return {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbohydrates': 0
        }
    else:
        return {
            'calories': food_log.servings * (
                food_log.custom_calories if food_log.custom_calories is not None else food_log.recipe.calories),
            'protein': food_log.servings * (
                food_log.custom_protein if food_log.custom_protein is not None else food_log.recipe.protein),
            'fat': food_log.servings * (
                food_log.custom_fat if food_log.custom_fat is not None else food_log.recipe.fat),
            'carbohydrates': food_log.servings * (
                food_log.custom_carbohydrates if food_log.custom_carbohydrates is not None else food_log.recipe.carbohydrates)
        }

def get_day_macros(user:User,date) -> dict:
    food_logs=FoodLog.objects.filter(user=user,date__date=date)

    return {
        'calories':sum(get_entry_macros(log)['calories'] for log in food_logs),
        'protein': sum(get_entry_macros(log)['protein'] for log in food_logs),
        'fat': sum(get_entry_macros(log)['fat'] for log in food_logs),
        'carbohydrates': sum(get_entry_macros(log)['carbohydrates'] for log in food_logs)
    }

def get_certain_food_log(user:User, date):
    food_logs=FoodLog.objects.filter(user=user,date__date=date).select_related('recipe')

    return [
        {
            'recipe_title':val(log.custom_title,log.recipe.title),
            'serving':log.servings,
            'meal_type':log.meal_type.capitalize(),
            'macroelement':get_entry_macros(log),
        }
        for log in food_logs
    ]