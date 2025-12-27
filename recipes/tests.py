from django.test import TestCase
from domain.food_log import *
from recipes.models import *
from django.contrib.auth.models import User
# Create your tests here.

class GetEntryMacrosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test','test@test.com','1234')
        cls.recipe=Recipe.objects.create(
            title='Pizza',
            calories=600, protein=100, carbohydrates=45, fat=10,
            servings=2,
            created_by=cls.user,
        )

    def test_use_recipe_value_when_no_custom(self):
        entry=FoodLog.objects.create(
            user=self.user,
            meal_type=MealType.BREAKFAST,
            recipe=self.recipe,
            servings=3,
        )
        macros=get_entry_macros(entry)
        self.assertEqual(macros['calories'],3*600)


    def test_use_recipe_value_when_custom_present(self):
        entry=FoodLog.objects.create(
            user=self.user,
            meal_type=MealType.DINNER,
            recipe=self.recipe,
            custom_calories=500,
            servings=3,
        )
        macros=get_entry_macros(entry)
        self.assertEqual(macros['calories'],3*500)

    def test_get_certain_food_log(self):
        entry = FoodLog.objects.create(
            user=self.user,
            meal_type=MealType.BREAKFAST,
            recipe=self.recipe,
            servings=3,
        )
        entry = FoodLog.objects.create(
            user=self.user,
            meal_type=MealType.BREAKFAST,
            recipe=self.recipe,
            servings=1,
            custom_calories=500,
            custom_title='PICCA'
        )
        from datetime import date
        results=get_certain_food_log(user=self.user,date=date.today(),meal_type=MealType.BREAKFAST)
        self.assertEqual(results[0]['macroelement']['calories'],3*600)
        self.assertEqual(results[1]['macroelement']['calories'], 1 * 500)
        self.assertEqual(results[1]['recipe_title'],'PICCA')

class GetDayMacrosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=User.objects.create_user('test2','test2@test.com','12345')
        cls.recipe=Recipe.objects.create(
            title='Pizza',
            calories=600, protein=100, carbohydrates=45, fat=10,
            servings=2,
            created_by=cls.user,
        )

        FoodLog.objects.create(
            user=cls.user,
            meal_type=MealType.SUPPER,
            recipe=cls.recipe,
            servings=2,
        )
        FoodLog.objects.create(
            user=cls.user,
            meal_type=MealType.BREAKFAST,
            recipe=cls.recipe,
            custom_calories=200,
            servings=1,
        )
        FoodLog.objects.create(
            user=cls.user,
            meal_type=MealType.BREAKFAST,
            recipe=cls.recipe,
            custom_calories=300,
            servings=2,
        )

    def test_get_day_macros(self):
        from domain.food_log import get_day_macros
        from datetime import date
        macros=get_day_macros(self.user,date=date.today())
        self.assertEqual(macros['calories'],2*600+1*200+2*300)