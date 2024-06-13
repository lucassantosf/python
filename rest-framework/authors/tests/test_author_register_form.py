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
        ('username',(
            'Username must have letters, numbers or one of those',
            'The length should be between 4 and 150 characters.',
        )),
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
        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))

    def test_username_field_min_length_should_be_4(self):
        self.form_data['username'] = 'joa'
        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = 'Username must have at least 4 characters'
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A' * 151
        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = 'Username must have less than 150 characters'
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_password_field_have_lower_upper_case_letters_and_numbers(self):
        self.form_data['password'] = 'Abc1234'
        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = (
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. The length should be '
            'at least 8 characters.'
        )
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('password'))

        self.form_data['password'] = '@saSSSdasAbc1234'
        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = (
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. The length should be '
            'at least 8 characters.'
        )
        self.assertNotIn(msg, response.content.decode('utf-8'))
        self.assertNotIn(msg, response.context['form'].errors.get('password'))

    def test_password_and_password_confirmation_are_equal(self):
        self.form_data['password'] = 'Abc1234'
        self.form_data['password_confirmation'] = 'Abc12343'

        url = reverse("authors:register_create")
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = 'Password and password_confirmation must be equal'
        
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('password'))

    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse("authors:register_create")
        response = self.client.get(url)

        self.assertEqual(response.status_code,404)

    def test_email_field_must_be_unique(self):
        url = reverse("authors:register_create")

        self.client.post(url,data = self.form_data, follow=True)
        response = self.client.post(url,data = self.form_data, follow=True)

        msg = 'User email is already in use'
        self.assertIn(msg,response.context['form'].errors.get('email'))
        self.assertIn(msg, response.content.decode('utf-8'))

    def test_author_created_can_login(self):
        url = reverse("authors:register_create")
        self.form_data.update({
            'username':'testuser',
            'password': '1q2w3e$R',
            'password_confirmation': '1q2w3e$R',
        })
        self.client.post(url,data = self.form_data, follow=True)
        is_autenticated = self.client.login(
            username='testuser',
            password='1q2w3e$R'
        )
        self.assertTrue(is_autenticated)