from django.db import models
from users.models import User
# Create your models here.

class Recipe (models.Model):
    title=models.CharField()
    spoonacular_id=models.IntegerField(unique=True,null=True)

    calories=models.DecimalField()
    protein=models.DecimalField()
    carbohydrates=models.DecimalField()
    fat=models.DecimalField()

    instructions=models.TextField()
    image_url=models.URLField()

    serving=models.IntegerField()
    is_vegetarian=models.BooleanField()
    is_vegan=models.BooleanField()
    is_gluten_free=models.BooleanField()
    is_custom=models.BooleanField()
    created_by=models.ForeignKey(User,null=True)
    created_at=models.DateTimeField()
