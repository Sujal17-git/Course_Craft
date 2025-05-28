from django import forms
from account.models import User
from .models import Section, Resource, Assignment

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'resource_type', 'file', 'link']
        widgets = {
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')

        if resource_type == 'file' and not file:
            raise forms.ValidationError("A file is required for file-type resources.")
        if resource_type == 'link' and not link:
            raise forms.ValidationError("A URL is required for link-type resources.")
        if resource_type == 'file' and link:
            cleaned_data['link'] = None
        if resource_type == 'link' and file:
            cleaned_data['file'] = None
        return cleaned_data

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'instructions', 'file']
        widgets = {
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("A title is required for the assignment.")
        return cleaned_data