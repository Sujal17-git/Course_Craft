from django import forms
from account.models import User

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
