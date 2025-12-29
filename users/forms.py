from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import UserProfile


class SingUpForm(UserCreationForm):
    email=forms.EmailField(max_length=100)
    class Meta:
        model=User
        fields=['username','password1','password2','email']


class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields=['weight','height','birth_date','gender','activity_level','target_weight','goal_date']

        widgets={
            'weight':forms.NumberInput(attrs={
                'class':'form-control',
                'placeholder': 'Weight (kg)',
                'step':'0.01'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.01'
            }),
            'birth_date': forms.DateInput(attrs={
                'type':'date',
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.01'
            }),
            'gender':forms.Select(attrs={'class':'form-select'}),
            'activity_level':forms.Select(attrs={'class':'form-select'}),
            'target_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.01'
            }),
            'goal_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = [('', 'Select your gender')] + list(self.fields['gender'].choices)[1:]
        self.fields['activity_level'].choices = [('', 'Select your activity level')] + list(
            self.fields['activity_level'].choices)[1:]