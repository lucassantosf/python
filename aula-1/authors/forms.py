from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        ]
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'password': 'Password',
        }
        help_texts = {
            'email': 'The e-mail must be valid'
        }
        error_messages = {
            'username': {
                'required': 'This field must not be empty',
                'max_length': 'This field must have less than',
                'invalid': 'This field is invalid',
            }
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Type your username here'
            }),
        }