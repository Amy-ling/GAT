from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.urls import reverse
from .models import UserProfile
from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm

class UserProfileModelTest(TestCase):
    """Test suite for the UserProfile model."""

    def setUp(self):
        """Set up a user and profile for testing."""
        self.user = User.objects.create_user(username='98765432', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            phone='98765432'
        )

    def test_profile_creation(self):
        """Test that a UserProfile can be created and linked to a User."""
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(self.user.profile, self.profile)
        self.assertEqual(self.profile.name, 'Test User')

    def test_profile_str_representation(self):
        """Test the string representation of the UserProfile."""
        self.assertEqual(str(self.profile), 'Test User')

    def test_phone_uniqueness(self):
        """Test that the phone number must be unique."""
        another_user = User.objects.create_user(username='11223344', password='password123')
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                user=another_user,
                name='Another User',
                phone='98765432' # Same phone number
            )

class UserViewsTest(TestCase):
    """Test suite for the views in the users app."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='98765432', password='password123')
        self.user_profile = UserProfile.objects.create(user=self.user, name='Test User', phone='98765432')
        
        self.admin_user = User.objects.create_user(username='12345678', password='password123')
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, name='Admin User', phone='12345678', is_admin=True)

    def test_gat_index_anonymous(self):
        """Test index view for an anonymous user, including search/filter context."""
        response = self.client.get(reverse('gat_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        
        # Verify that the context for search and filtering is present
        self.assertIn('items', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('selected_category', response.context)
        self.assertIn('query', response.context)
        self.assertTrue(response.context['guest'])

    def test_gat_index_logged_in_user(self):
        """Test index view for a logged-in regular user."""
        self.client.login(username='98765432', password='password123')
        response = self.client.get(reverse('gat_index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('items:user_main'))

    def test_register_view(self):
        """Test the user registration view."""
        response = self.client.get(reverse('users:register_view'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('users:register_view'), {
            'phone': '55667788',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='55667788').exists())

    def test_login_logout_view(self):
        """Test user login and logout."""
        # Test login - A successful login should redirect to the user's portal page.
        response = self.client.post(reverse('users:login'), {'username': '98765432', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:gat_portal'))

        # Test logout
        self.client.login(username='98765432', password='password123')
        response = self.client.get(reverse('users:logout')) # Use GET for logout link
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/logout.html')

    def test_profile_view(self):
        """Test that a logged-in user can view and update their profile."""
        self.client.login(username='98765432', password='password123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

        # Test valid profile update
        response = self.client.post(reverse('users:profile'), {
            'name': 'Updated Name',
            'phone': self.user_profile.phone  # Include the phone number
        })
        self.assertEqual(response.status_code, 302) # Successful update redirects
        self.assertRedirects(response, reverse('users:profile'))
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.name, 'Updated Name')

    def test_sysadmin_reset_pwd_access(self):
        """Test access control for the sysadmin password reset page."""
        self.client.login(username='98765432', password='password123')
        response = self.client.get(reverse('users:systemadmin_reset_pwd'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('items:user_main'))

        self.client.login(username='12345678', password='password123')
        response = self.client.get(reverse('users:systemadmin_reset_pwd'))
        self.assertEqual(response.status_code, 200)


class UserFormsTest(TestCase):
    """Test suite for the forms in the users app."""

    def setUp(self):
        """Set up a user for form tests."""
        self.user = User.objects.create_user(username='98765432', password='password123')
        self.profile = UserProfile.objects.create(user=self.user, name='Test User', phone='98765432')

    # Tests for UserRegisterForm
    def test_register_form_valid_data(self):
        """Test UserRegisterForm with valid data."""
        form_data = {
            'phone': '11223344',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_password_mismatch(self):
        """Test UserRegisterForm with mismatching passwords."""
        form_data = {
            'phone': '11223344',
            'password': 'a_valid_password1',
            'password2': 'a_different_password',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'][0], "Passwords don't match.")

    def test_register_form_phone_already_exists(self):
        """Test UserRegisterForm with a phone number that already exists."""
        form_data = {
            'phone': '98765432',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
        self.assertEqual(form.errors['phone'][0], "Phone number has been registered")

    def test_register_form_invalid_phone_not_digit(self):
        """Test UserRegisterForm with a non-digit phone number."""
        form_data = {
            'phone': 'abcdefgh',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
        self.assertEqual(form.errors['phone'][0], "Phone number must be digits")

    def test_register_form_invalid_phone_length(self):
        """Test UserRegisterForm with a phone number of incorrect length."""
        form_data = {
            'phone': '12345',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_register_form_weak_password(self):
        """Test UserRegisterForm with a weak password."""
        form_data = {
            'phone': '11223344',
            'password': '123',
            'password2': '123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_register_form_save_method(self):
        """Test the save method of the UserRegisterForm."""
        form_data = {
            'phone': '11223344',
            'password': 'a_valid_password1',
            'password2': 'a_valid_password1',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertTrue(User.objects.filter(username='11223344').exists())
        self.assertTrue(UserProfile.objects.filter(phone='11223344').exists())
        profile = UserProfile.objects.get(phone='11223344')
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.name, '11223344')
        self.assertFalse(profile.is_admin)

    # Tests for UserLoginForm
    def test_login_form_valid(self):
        """Test the UserLoginForm with valid data."""
        form_data = {'username': '98765432', 'password': 'password123'}
        from django.test import RequestFactory
        request = RequestFactory().post('/login/')
        request.user = self.user
        form = UserLoginForm(data=form_data, request=request)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_credentials(self):
        """Test UserLoginForm with invalid credentials."""
        form_data = {'username': '98765432', 'password': 'wrongpassword'}
        from django.test import RequestFactory
        request = RequestFactory().post('/login/')
        request.user = self.user
        form = UserLoginForm(data=form_data, request=request)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_login_form_invalid_phone_not_digit(self):
        """Test UserLoginForm with a non-digit username."""
        form_data = {'username': 'abcdefgh', 'password': 'password123'}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "Phone number must be digits.")

    # Tests for UserProfileUpdateForm
    def test_profile_update_form_valid(self):
        """Test the UserProfileUpdateForm with valid data."""
        form_data = {
            'name': 'New Name',
            'phone': self.profile.phone  # Include the phone number
        }
        form = UserProfileUpdateForm(instance=self.profile, data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'New Name')

    def test_profile_update_form_blank_name(self):
        """Test UserProfileUpdateForm with a blank name."""
        form_data = {'name': ''}
        form = UserProfileUpdateForm(instance=self.profile, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
