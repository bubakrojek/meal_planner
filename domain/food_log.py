from functools import reduce

from django.contrib.auth.models import User

from recipes.models import Recipe, FoodLog, MealType


def val(custom, original):
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


def get_day_macros(user: User, date) -> dict:
    food_logs_type = [(
        meal_type.value,
        FoodLog.objects.filter(user=user, date=date, meal_type=meal_type.value)
    ) for meal_type in MealType]

    def sum_macros(logs):
        if not logs.exists():
            return {'calories': 0, 'protein': 0, 'fat': 0, 'carbohydrates': 0}
        else:
            macroelements_list = list(map(get_entry_macros, logs))

            return reduce(
                lambda acc, item: {
                    'calories': acc['calories'] + item['calories'],
                    'protein': acc['protein'] + item['protein'],
                    'fat': acc['fat'] + item['fat'],
                    'carbohydrates': acc['carbohydrates'] + item['carbohydrates']
                },
                macroelements_list,
                {'calories': 0, 'protein': 0, 'fat': 0, 'carbohydrates': 0}
            )

    return dict(
        map(
            lambda item: (item[0], sum_macros(item[1])),
            food_logs_type
        )
    )


def get_certain_food_log(user: User, date):
    food_logs_types = [(
    meal_type.value, FoodLog.objects.filter(user=user, date=date, meal_type=meal_type.value).select_related('recipe')
    )for meal_type in MealType]

    flat_logs = [
        (
            food_logs[0],
            {
                'recipe_title': log.custom_title if log.recipe is None else log.recipe.title if log.custom_title is None else val(
                    log.custom_title, log.recipe.title),
                'serving': log.servings,
                'macroelement': get_entry_macros(log),
            }

        )
        for food_logs in food_logs_types
        for log in food_logs[1]
    ]

    result= reduce(
        lambda acc, item: {
            **acc,
            item[0]: acc.get(item[0], []) + [item[1]]
        },
        flat_logs,
        {}
    )
    for meal_type in MealType:
        if meal_type.value not in result:
            result[meal_type.value] = []

    return result

def get_recipes():
    recipes = Recipe.objects.all()
    return {
        'recipes': recipes,
    }
