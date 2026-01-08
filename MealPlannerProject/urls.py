"""
URL configuration for MealPlannerProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from recipes import certain_food_log, add_food_log, delete_food_log, update_food_log, search_recipes_htmx, \
    weekly_meal_plan_view, generate_meal_plan, regenerate_day, execute_daily_plan
from users.views import show_my_profile, register, sign_in, logout_view, complete_profile, complete_dietary_preferences, \
    add_weight_log, show_weight_logs, delete_weight_log, update_weight_log

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', certain_food_log, name='food_logs'),

    path('profile/', show_my_profile, name='show_my_profile'),

    path('register/', register, name='register'),
    path('sign_in/', sign_in, name='sign_in'),
    path('logout/', logout_view, name='logout'),

    path('complete_profile/', complete_profile, name='complete_profile'),
    path('complete_dietary_preferences/', complete_dietary_preferences, name='complete_dietary_preferences'),

    path('food_log/<str:date>/<str:meal_type>/add', add_food_log, name='add_food_log'),
    path('search_recipes_htmx/', search_recipes_htmx, name='search_recipes_htmx'),
    path('food_logs/', certain_food_log, name='food_logs'),
    path('delete_food_log/<int:log_id>/', delete_food_log, name='delete_food_log'),
    path('update_food_log/<int:log_id>/', update_food_log, name='update_food_log'),

    path('show_weight_logs/', show_weight_logs, name='show_weight_logs'),
    path('add_weight_log/', add_weight_log, name='add_weight_log'),
    path('delete_weight_log/<int:log_id>/', delete_weight_log, name='delete_weight_log'),
    path('update_weight_log/<int:log_id>/', update_weight_log, name='update_weight_log'),

    path('meal_plan/', weekly_meal_plan_view, name='meal_plan'),
    path('meal_plan/generate/', generate_meal_plan, name='generate_meal_plan'),

    path('meal_plan/regenerate_day/<str:date_str>/', regenerate_day, name='regenerate_day'),
    path('meal_plan/execute/<str:date_str>/', execute_daily_plan, name='execute_daily_plan')
]
