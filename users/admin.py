from django.contrib import admin
from .models import UserProfile, WeightLog, Macronutrients, DietaryPreferences

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(WeightLog)
admin.site.register(Macronutrients)
admin.site.register(DietaryPreferences)

