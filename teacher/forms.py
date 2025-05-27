from django import forms
from account.models import User
from .models import Section
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

# forms.py



class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

