import decimal


# using the Mifflin-St Jeor equation
def calculate_bmr(gender: str, weight: float, height: int,
                  age: int) -> float:
    if gender == 'M':
        return (10.0 * weight) + (6.25 * height) - (5.0 * age) + 5
    else:
        return (10.0 * weight) + (6.25 * height) - (5.0 * age) - 161


# using the Mifflin-St Jeor equation
def calculate_tdee(bmr: float, activity_level: str) -> float:
    if activity_level == '1':
        return bmr * 1.2
    elif activity_level == '2':
        return bmr * 1.375
    elif activity_level == '3':
        return bmr * 1.55
    elif activity_level == '4':
        return bmr * 1.725
    else:
        return bmr * 1.9


def calculate_protein(activity_level: str, weight: decimal) -> float:
    if activity_level == '1' or activity_level == '2':
        return weight * 1.1
    else:
        return weight * 1.8


def calculate_fat(weight: decimal) -> float:
    return 0.8 * weight


def calculate_carbohydrates(tdee: float) -> float:
    return (0.45 * tdee) / 4.0


def calculate_target_macros(activity_level: str, weight: decimal,tdee: float, bmr: float)->dict:
    return {
        'calories':calculate_tdee(bmr,activity_level),
        'protein':calculate_protein(activity_level,weight),
        'fat':calculate_fat(weight),
        'carbohydrates':calculate_carbohydrates(tdee)
    }
