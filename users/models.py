from datetime import date

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class DietaryPreferences(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, related_name='dietary_preferences')

    is_vegan=models.BooleanField(default=False)
    is_vegetarian=models.BooleanField(default=False)
    is_gluten_free=models.BooleanField(default=False)
    is_diary_free=models.BooleanField(default=False)
    is_keto=models.BooleanField(default=False)

    #TODO excluded ingredients

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Preferences for {self.user.username}'

class WeightLog(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name='weight_logs')
    date=models.DateField()
    weight=models.DecimalField(max_digits=5,decimal_places=2)
    notes=models.TextField(blank=True)

    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-date']
        unique_together=['user','date']

    def __str__(self):
        return f'{self.user.username}  - {self.weight} at {self.date}'


class Macronutrients(models.Model):
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    protein = models.DecimalField(max_digits=6, decimal_places=2)  # gramy
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2)  # gramy
    fat = models.DecimalField(max_digits=6, decimal_places=2)


class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'


class ActivityLevel(models.TextChoices):
    SEDENTARY = '1', 'Sedentary (little or no exercise)'
    LIGHTLY_ACTIVE = '2', 'Lightly active (exercise 1-3 days/week)'
    MODERATELY_ACTIVE = '3', 'Moderately active (exercise 3-5 days/week)'
    VERY_ACTIVE = '4', 'Very active (exercise 6-7 days/week)'
    EXTRA_ACTIVE = '5', 'Extra active (physical job or training twice/day)'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    weight = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.IntegerField()
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)

    activity_level = models.CharField(max_length=1, choices=ActivityLevel.choices)

    target_weight = models.DecimalField(max_digits=5, decimal_places=2)  # planowana waga
    goal_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    target_macros = models.ForeignKey(Macronutrients, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='user_profiles')

    def __str__(self):
        return f"{self.user.username}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def bmr(self):
        from domain.nutritions import calculate_bmr
        return calculate_bmr(self.gender, float(self.weight), self.height, self.age)

    @property
    def tdee(self):
        from domain.nutritions import calculate_tdee
        return calculate_tdee(self.bmr, self.activity_level)

    @property
    def macronutrients(self):

        if self.target_macros:
            return {
                'calories': float(self.target_macros.calories),
                'protein': float(self.target_macros.protein),
                'fat': float(self.target_macros.fat),
                'carbohydrates': float(self.target_macros.carbohydrates)
            }

        else:
            from domain.nutritions import calculate_target_macros
            macroelements = calculate_target_macros(self.activity_level, float(self.weight), self.tdee, self.bmr)
            macroelements_obj=Macronutrients.objects.create(
                calories=macroelements['calories'],
                protein=macroelements['protein'],
                fat=macroelements['fat'],
                carbohydrates=macroelements['carbohydrates']
            )

            self.target_macros=macroelements_obj
            self.save(update_fields=['target_macros'])
            return macroelements
