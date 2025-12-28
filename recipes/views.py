from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from domain.food_log import get_certain_food_log, get_day_macros


# Create your views here.

@login_required
def certain_food_log(request: HttpRequest) -> HttpResponse:
    date_str = request.GET.get('date')

    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.today()
    else:
        date = datetime.today()

    dates = [date + timedelta(days=i) for i in range(-3, 4)]

    food_logs = get_certain_food_log(user=request.user, date=date)
    day_macros = get_day_macros(user=request.user, date=date)

    return render(request, 'food_logs/certain_food_log.html', {
        'user': request.user,
        'food_logs': food_logs,
        'day_macros': day_macros,
        'dates': dates,
    })
