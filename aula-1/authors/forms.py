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
        add_placeholder(self.fields['password'], 'Your password')
        add_placeholder(self.fields['password_confirmation'], 'Repeat your password')

    username = forms.CharField(
        label='Username',
        error_messages={
            'required': 'This field must not be empty',
            'min_length': 'Username must have at least 4 characters',
            'max_length': 'Username must have less than 150 characters'
        },
        help_text = (
            'Username must have letters, numbers or one of those',
            'The length should be between 4 and 150 characters.',
        ),
        min_length=4,
        max_length=150
    )
    first_name = forms.CharField(
        error_messages={'required': 'Write your first name'},
        label='First Name'
    )
    last_name = forms.CharField(
        error_messages={'required': 'Write your last name'},
        label='Last Name'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Password is required'
        },
        help_text = ('Password must have at least 6 chars'),
        validators=[strong_password],
        label='Password'
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Password confirmation is required'
        },
        label='Password Confirmation'
    )
    email = forms.EmailField(
        error_messages={
            'required': 'Email is required'
        },
        label='Email',
        help_text = 'The e-mail must be valid'
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

    def clean_email(self):
        email = self.cleaned_data.get('email','')
        exists = User.objects.filter(email=email)

        if exists:
            raise ValidationError('User email is already in use', code='invalid')

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise ValidationError({
                'password':'Password and password_confirmation must be equal'
            })