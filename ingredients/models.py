from django.db import models
from recipes.models import Recipe
# Create your models here.
class Ingredient (models.Model):
    recipe=models.ForeignKey(Recipe,null=True,blank=True,on_delete=models.CASCADE,related_name='ingredients')

    title = models.CharField(max_length=200)
    calories = models.DecimalField(max_digits=5,decimal_places=2)
    protein = models.DecimalField(max_digits=5,decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=5,decimal_places=2)
    fat = models.DecimalField(max_digits=5,decimal_places=2)

    amount=models.DecimalField(max_digits=5,decimal_places=2)
    unit=models.CharField(max_length=50)