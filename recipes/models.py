from django.db import models
from users.models import User
# Create your models here.

class Recipe (models.Model):
    title=models.CharField(max_length=300)
    spoonacular_id=models.IntegerField(unique=True,null=True)

    calories=models.DecimalField(max_digits=6,decimal_places=2)
    protein=models.DecimalField(max_digits=5,decimal_places=2)
    carbohydrates=models.DecimalField(max_digits=5,decimal_places=2)
    fat=models.DecimalField(max_digits=5,decimal_places=2)

    instructions=models.TextField(blank=True,max_length=500)
    image_url=models.URLField()

    serving=models.IntegerField()
    is_vegetarian=models.BooleanField(default=False)
    is_vegan=models.BooleanField(default=False)
    is_gluten_free=models.BooleanField(default=False)
    is_custom=models.BooleanField(default=False)
    created_by=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    created_at=models.DateTimeField()

class Ingredient (models.Model):
    recipe=models.ForeignKey(Recipe,null=True,blank=True,on_delete=models.CASCADE,related_name='ingredients')

    title = models.CharField(max_length=200)
    calories = models.DecimalField(max_digits=5,decimal_places=2)
    protein = models.DecimalField(max_digits=5,decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=5,decimal_places=2)
    fat = models.DecimalField(max_digits=5,decimal_places=2)

    amount=models.DecimalField(max_digits=5,decimal_places=2)
    unit=models.CharField(max_length=50)