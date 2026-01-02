from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import UserProfile, DietaryPreferences


class SingUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']


class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['weight', 'height', 'birth_date', 'gender', 'activity_level', 'target_weight', 'goal_date']

        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.01'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height (cm)',
                'step': '0.01'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'text',
                'onfocus':"(this.type='date')",
                'class': 'form-control',
                'placeholder': 'Birth Date',
                'step': '0.01'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
            'target_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target Weight (kg)',
                'step': '0.01'
            }),
            'goal_date': forms.DateInput(attrs={
                'type': 'text',
                'onfocus':"(this.type='date')",
                'class': 'form-control',
                'placeholder': 'Goal Date',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = [('', 'Select your gender')] + list(self.fields['gender'].choices)[1:]
        self.fields['activity_level'].choices = [('', 'Select your activity level')] + list(
            self.fields['activity_level'].choices)[1:]


class CompleteDietaryPreferences(forms.ModelForm):
    class Meta:
        model = DietaryPreferences
        fields = ['is_vegan', 'is_vegetarian', 'is_gluten_free', 'is_dairy_free', 'is_keto']

        widgets = {
            'is_vegan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_gluten_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_dairy_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_keto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'is_vegan': 'Vegan',
            'is_vegetarian': 'Vegetarian',
            'is_gluten_free': 'Gluten Free',
            'is_dairy_free': 'Dairy Free',
            'is_keto': 'Keto',
        }
