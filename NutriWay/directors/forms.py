from django import forms
from .models import SpecialistRequest

class SpecialistRequestForm(forms.ModelForm):
    class Meta:
        model = SpecialistRequest
        fields = ['status', 'feedback']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        feedback = cleaned_data.get('feedback')

        if status == 'rejected' and not feedback:
            self.add_error('feedback', "Feedback is required when rejecting the request.")

        return cleaned_data
