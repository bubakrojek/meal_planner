from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Recipe (models.Model):
    spoonacular_id=models.IntegerField(unique=True,null=True)

    title=models.CharField(max_length=300)
    ingredients_text = models.TextField(blank=True)
    calories=models.DecimalField(max_digits=6,decimal_places=2)
    protein=models.DecimalField(max_digits=5,decimal_places=2)
    carbohydrates=models.DecimalField(max_digits=5,decimal_places=2)
    fat=models.DecimalField(max_digits=5,decimal_places=2)

    instructions=models.TextField(blank=True)
    image_url=models.URLField()

    servings=models.IntegerField()
    is_vegetarian=models.BooleanField(default=False)
    is_vegan=models.BooleanField(default=False)
    is_gluten_free=models.BooleanField(default=False)
    is_custom=models.BooleanField(default=False)
    created_by=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Ingredient (models.Model):
    recipe=models.ForeignKey(Recipe,on_delete=models.CASCADE,related_name='ingredients')

    title = models.CharField(max_length=200)

    amount=models.DecimalField(max_digits=5,decimal_places=2)
    unit=models.CharField(max_length=50)

    def __str__(self):
        return self.title

class MealType(models.TextChoices):
    BREAKFAST='breakfast'
    LUNCH='lunch'
    DINNER='dinner'
    SNACK='snack'
    SUPPER='supper'


class FoodLog(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='logs')

    date=models.DateField()
    meal_type=models.CharField(max_length=20,choices=MealType.choices)

    recipe=models.ForeignKey(Recipe,blank=True,null=True,on_delete=models.CASCADE)

    custom_title = models.CharField(blank=True,null=True,max_length=300)

    custom_calories = models.DecimalField(blank=True,null=True,max_digits=6, decimal_places=2)
    custom_protein = models.DecimalField(blank=True,null=True,max_digits=5, decimal_places=2)
    custom_carbohydrates = models.DecimalField(blank=True,null=True,max_digits=5, decimal_places=2)
    custom_fat = models.DecimalField(blank=True,null=True,max_digits=5, decimal_places=2)

    servings = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        if self.custom_title is None:
            return f"{self.user.__str__()} {self.date} {self.recipe.title}"
        else:
            return f"{self.user.__str__()} {self.date} {self.custom_title}"


class PlannedMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planned_meals')

    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MealType.choices)

    recipe = models.ForeignKey(Recipe, blank=True, null=True, on_delete=models.CASCADE)

    ingredients_snapshot = models.JSONField(null=True,blank=True)
    custom_title = models.CharField(blank=True, null=True, max_length=300)

    custom_calories = models.DecimalField(blank=True, null=True, max_digits=6, decimal_places=2)
    custom_protein = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    custom_carbohydrates = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    custom_fat = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)

    servings = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'meal_type']
        unique_together = ['user', 'date', 'meal_type']

    def __str__(self):
        if self.custom_title is None:
            return f"{self.user.__str__()} {self.date} {self.recipe.title}"
        else:
            return f"{self.user.__str__()} {self.date} {self.custom_title}"
