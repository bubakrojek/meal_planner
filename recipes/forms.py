from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from recipes.models import FoodLog


class FoodLogForm(forms.ModelForm):
    class Meta:
        model = FoodLog
        fields = ['recipe', 'custom_title', 'custom_calories', 'custom_protein', 'custom_carbohydrates', 'custom_fat','servings']

        widgets = {
            #'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'recipe': forms.Select(attrs={'class': 'form-select'}),
            'custom_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom title',

            }),
            'custom_calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom calories.',
                'step': '1',
                'min':'0',
                'max':'9999'
            }),
            'custom_protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom protein.',
                'step': '1',
                'min': '0',
                'max': '9999'
            }),
            'custom_carbohydrates': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom carbohydrates.',
                'step': '1',
                'min': '0',
                'max': '9999'
            }),
            'custom_fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Custom fat',
                'step': '1',
                'min': '0',
                'max': '9999'
            }),
            'servings': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Servings',
                'step': '1',
                'min': '0',
                'max': '100'
            }),

        }

    def clean(self):
        cleaned_data = super().clean()

        recipe_source = self.data.get('recipe_source')

        if recipe_source == 'database':
            if not cleaned_data.get('recipe'):
                raise forms.ValidationError('Please select a recipe from your database.')
        elif recipe_source == 'api':
            if not self.data.get('api_recipe_title'):
                raise forms.ValidationError('Please select a recipe from API search results.')
        elif recipe_source == 'custom':
            required_custom = ['custom_title', 'custom_calories', 'custom_protein',
                               'custom_carbohydrates', 'custom_fat']
            if not all(cleaned_data.get(field) is not None for field in required_custom):
                raise forms.ValidationError(
                    'Please fill all custom meal fields: title, calories, protein, carbs, and fat.'
                )

        return cleaned_data


    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
        #self.fields['meal_type'].choices = [('', 'Select your gender')] + list(self.fields['meal_type'].choices)[1:]
