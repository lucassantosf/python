import re 

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def add_attr(field,attr_name,attr_new_val):
    existing_attr = field.widget.attrs.get(attr_name,'')
    field.widget.attrs[attr_name] = f'{existing_attr} {attr_new_val}'.strip()

def add_placeholder(field, placeholder_val):
    add_attr(field, 'placeholder', placeholder_val)

def strong_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')

    if not regex.match(password):
        raise ValidationError((
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. The length should be '
            'at least 8 characters.'
        ),
            code='invalid'
        )


class RegisterForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        add_placeholder(self.fields['username'], 'Your username')
        add_placeholder(self.fields['email'], 'Your email')
        add_placeholder(self.fields['first_name'], 'Your first name')
        add_placeholder(self.fields['last_name'], 'Your last name')

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder':'Your password'}),
        error_messages={
            'required': 'Password is required'
        },
        help_text = ('Password must have at least 6 chars'),
        validators=[strong_password]
    )
    password_confirmation = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder':'Repeat your password'})
    )

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
            'password_confirmation': 'Password Confirmation'
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

    def clean_password(self):
        data = self.cleaned_data.get('password')

        if 'atencao' in data :
            raise ValidationError(
                'Não digite atencao na senha',
                code='invalid',
                params={'value':'atencao'}
            )

        return data

    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')

        if 'lucas' in data :
            raise ValidationError(
                'Nome inválido',
                code='invalid',
                params={'value':'lucas'}
            )

        return data

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise ValidationError({
                'password':'Password and password_confirmation must be equal'
            })