from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Resource


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['resource', 'date', 'start_time', 'end_time', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'step': 900}, format='%H:%M'),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'step': 900}, format='%H:%M'),
            'purpose': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Project meeting, thesis experiment...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resource'].queryset = Resource.objects.filter(is_active=True)
        self.fields['resource'].empty_label = '-- Select a resource --'


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'resource_type', 'location', 'capacity', 'manager', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=False, help_text='Research group / department')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.department = self.cleaned_data.get('department', '')
            user.profile.save()
        return user