# Meal Planner

> Django web application for meal planning with macronutrient tracking

![Python](https://img.shields.io/badge/python-3.11-blue)
![Django](https://img.shields.io/badge/django-5.2-green)
![Bootstrap](https://img.shields.io/badge/bootstrap-5.3-purple)

## About

Meal Planner uses Spoonacular API to automatically generate personalized weekly meal plans based on your goals, dietary preferences, and macronutrient requirements. Built with Django.

## Features

- Weekly meal plan generation (Spoonacular API)
- Daily food logging with 5 meal types
- TDEE calculation using Mifflin-St Jeor equation
- Weight tracking with interactive chart (Plotly.js)
- Recipe search and custom recipe creation
- Dietary preferences (vegan, vegetarian, keto, gluten-free, dairy-free)
- Real-time macro percentage tracking
- Dark mode UI with Bootstrap 5

## Tech Stack

- **Backend:** Python 3.11, Django 5.2, SQLite
- **Frontend:** Bootstrap 5.3, Plotly.js, HTMX
- **API:** Spoonacular Recipe & Nutrition API

## Installation

### Prerequisites

- Python 3.11+
- Spoonacular API key (free at https://spoonacular.com/food-api)

### Quick Start

  ```bash
  # Clone repository
  git clone https://github.com/bubakrojek/meal_planner.git
  cd MealPlannerProjectFolder
  
  # Setup environment
  python -m venv venv
  venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  
  # Configure API key in settings.py
  SPOONACULAR_API_KEY = 'your_key_here'
  
  # Run migrations
  python manage.py makemigrations
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  ```


## Usage

1. Register and complete your profile (weight, height, activity level, goals)
2. Set dietary preferences (optional)
3. Generate weekly meal plan via Spoonacular API
4. Copy planned meals to daily food logs or add custom entries
5. Track progress with weight logs and macro charts

## Project Structure

```
MealPlannerProject/
├── domain/                  
│   ├── food_log.py         
│   ├── meal_planning.py   
│   ├── recipe_api.py       
│   └── tdee.py             
├── users/                  
├── recipes/                
└── templates/             
```


## License

MIT License

## Author

**bubakrojek** - [@bubakrojek](https://github.com/bubakrojek)

