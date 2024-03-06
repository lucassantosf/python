from django.test import TestCase
from django.test import TestCase as DjangoTestCase
from authors.forms import RegisterForm
from parameterized import parameterized
from django.urls import reverse

class AuthorRegisterFormUnitTest(TestCase):

    @parameterized.expand([
        ('username','Your username'),
        ('email','Your email'),
        ('first_name','Your first name'),
        ('last_name','Your last name'),
        ('password','Your password'),
        ('password_confirmation','Repeat your password'),
    ])
    def test_fields_placeholder(self, field, placeholder):
        form = RegisterForm()
        current_placeholder = form[field].field.widget.attrs['placeholder']
        self.assertEqual(placeholder, current_placeholder)

    @parameterized.expand([
        ('email','The e-mail must be valid'),
        ('password','Password must have at least 6 chars'),
    ])
    def test_fields_help_text(self, field, needed):
        form = RegisterForm()
        current = form[field].field.help_text
        self.assertEqual(current, needed)

    @parameterized.expand([
        ('username','Username'),
        ('first_name','First Name'),
        ('last_name','Last Name'),
        ('email','Email'),
        ('password','Password'),
        ('password_confirmation','Password Confirmation'),
    ])
    def test_fields_label(self, field, needed):
        form = RegisterForm()
        current = form[field].field.label
        self.assertEqual(current, needed)

class AuthorRegisterFormIntegrationTest(DjangoTestCase):
    def setUp(self, *args, **kwargs):
        self.form_data = {
            'username': 'user',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email@gmail.com',
            'password': 'AaBbCc123',
            'password_confirmation': 'AaBbCc123',
        }
        return super().setUp(*args,**kwargs)

    @parameterized.expand([
        ('username','This field must not be empty'),
        ('first_name','Write your first name'),
        ('last_name','Write your last name'),
        ('password','Password is required'),
        ('password_confirmation','Password confirmation is required'),
        ('email','Email is required'),
    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse("authors:create")
        response = self.client.post(url,data = self.form_data, follow=True)

        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))