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
from django.urls import path, include
from recipes.views import certain_food_log
from users.views import show_my_profile, register, sign_in, logout_view, complete_profile, complete_dietary_preferences

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', certain_food_log, name='food_logs'),
    path('food_logs/',certain_food_log, name='food_logs'),
    path('profile/', show_my_profile, name='show_my_profile'),
    path('register/', register, name='register'),
    path('sign_in/',sign_in, name='sign_in'),
    path('logout/',logout_view,name='logout'),
    path('complete_profile/',complete_profile,name='complete_profile'),
    path('complete_dietary_preferences/',complete_dietary_preferences,name='complete_dietary_preferences')
]
