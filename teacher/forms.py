
from django import forms
from account.models import User
from .models import Section, Resource, Assignment, Poll, PollOption
from django.utils import timezone

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'resource_type', 'file', 'link']
        widgets = {
            'resource_type': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'file': forms.FileInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm'}),
            'link': forms.URLInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
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
            'instructions': forms.Textarea(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm'}),
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("A title is required for the assignment.")
        return cleaned_data

class PollForm(forms.ModelForm):
    option1 = forms.CharField(max_length=100, required=True, label="Option 1", widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}))
    option2 = forms.CharField(max_length=100, required=True, label="Option 2", widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}))
    option3 = forms.CharField(max_length=100, required=False, label="Option 3", widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}))
    option4 = forms.CharField(max_length=100, required=False, label="Option 4", widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}))
    option5 = forms.CharField(max_length=100, required=False, label="Option 5", widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}))
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        label="Deadline (IST)"
    )

    class Meta:
        model = Poll
        fields = ['question', 'deadline']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if not timezone.is_aware(deadline):
            deadline = timezone.make_aware(deadline, timezone.get_default_timezone())
        if deadline <= timezone.now():
            raise forms.ValidationError("Deadline must be in the future.")
        return deadline

    def save(self, commit=True, section=None, user=None):
        poll = super().save(commit=False)
        if section:
            poll.section = section
        if user:
            poll.created_by = user
        if commit:
            poll.save()
            options = [
                self.cleaned_data.get('option1'),
                self.cleaned_data.get('option2'),
                self.cleaned_data.get('option3'),
                self.cleaned_data.get('option4'),
                self.cleaned_data.get('option5'),
            ]
            for option_text in options:
                if option_text:
                    PollOption.objects.create(poll=poll, text=option_text)
        return poll
