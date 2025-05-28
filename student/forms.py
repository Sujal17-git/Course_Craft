from django import forms
from account.models import User
from .models import StudentAssignmentSubmission, PollResponse
from teacher.models import PollOption

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

class PollResponseForm(forms.ModelForm):
    option = forms.ModelChoiceField(queryset=PollOption.objects.none(), widget=forms.RadioSelect, empty_label=None)

    class Meta:
        model = PollResponse
        fields = ['option']

    def __init__(self, *args, **kwargs):
        poll = kwargs.pop('poll', None)
        super().__init__(*args, **kwargs)
        if poll:
            self.fields['option'].queryset = PollOption.objects.filter(poll=poll)