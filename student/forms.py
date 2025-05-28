from django import forms
from account.models import User
from .models import StudentAssignmentSubmission

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentAssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = StudentAssignmentSubmission
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("A file is required for submission.")
        return file