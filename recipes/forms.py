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
        recipe = cleaned_data.get('recipe')
        custom_title = cleaned_data.get('custom_title')


        if not recipe and not custom_title:
            raise forms.ValidationError('You must select a recipe or enter a custom meal name.')

        return cleaned_data


    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
        #self.fields['meal_type'].choices = [('', 'Select your gender')] + list(self.fields['meal_type'].choices)[1:]
