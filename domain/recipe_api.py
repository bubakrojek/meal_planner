from functools import reduce
from typing import List, Dict

import requests


def extract_nutrient_amount(recipe:dict, name:str)->float:
    nutrients=recipe.get('nutrition', {}).get('nutrients', [])
    return next(
        (n['amount'] for n in nutrients if n['name']==name),
        0
    )

def extract_ingredients(recipe:dict)->List[Dict]:
    ingredients=recipe.get('ingredients',[])

    return [
        {
            'name':ing.get('name','unknown'),
            'amount':ing.get('amount',1),
            'unit':ing.get('unit','piece')
        }
        for ing in ingredients
    ]

def aggregate_ingredients(ingredients:List[Dict])->Dict[str,Dict]:

    def group_reducer(acc:Dict,ing:Dict)->Dict:
        name=ing['name'].lower().strip()
        unit=ing['unit']

        if name not in acc:
            acc[name]={
                'name':name.title(),
                'unit':unit,
                'total_amount':0,
            }

        acc[name]['total_amount']+=ing['amount']
        return acc

    return reduce(group_reducer,ingredients,{})

def search_recipes_api(query:str, api_key: str, number:int=10) -> List[Dict]:
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': query,
        'number': number,
        'addRecipeNutrition': True,
        'apiKey': api_key
    }

    try:
        response=requests.get(url,params=params)
        response.raise_for_status()
        results=response.json().get('results',[])

        return list(map(
            lambda r: {
                'id':r['id'],
                'title':r['title'],
                'calories':extract_nutrient_amount(r,'Calories'),
                'protein': extract_nutrient_amount(r, 'Protein'),
                'carbohydrates': extract_nutrient_amount(r, 'Carbohydrates'),
                'fat': extract_nutrient_amount(r, 'Fat'),
            },
            results
        ))

    except requests.RequestException:
        return []