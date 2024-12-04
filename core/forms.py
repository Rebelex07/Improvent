from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Seleccionar archivo CSV",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )        