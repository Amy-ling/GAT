from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from .models import LogBook
from .services import create_log

class LogBookModelTest(TestCase):
    """Test suite for the LogBook model."""

    def setUp(self):
        """Set up a user for testing."""
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_log_creation(self):
        """Test that a log entry can be created successfully."""
        log = LogBook.objects.create(
            log_user=self.user,
            log_action="User logged in",
            log_result="success"
        )
        self.assertEqual(LogBook.objects.count(), 1)
        self.assertEqual(log.log_user, self.user)
        self.assertEqual(log.log_action, "User logged in")
        self.assertTrue(str(log.log_date) in str(log))

    def test_user_deletion_sets_log_user_to_null(self):
        """Test that deleting a User sets the log_user field to NULL."""
        log = LogBook.objects.create(log_user=self.user, log_action="Test Action")
        self.assertIsNotNone(log.log_user)
        
        # Delete the user
        self.user.delete()
        
        # Refresh the log instance from the database
        log.refresh_from_db()
        
        self.assertIsNone(log.log_user)


class LogServicesTest(TestCase):
    """Test suite for the log services."""

    def setUp(self):
        """Set up a user and an anonymous user for testing."""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.anonymous_user = AnonymousUser()

    def test_create_log_with_authenticated_user(self):
        """Test create_log with an authenticated user."""
        create_log(self.user, "Performed an action")
        log = LogBook.objects.first()
        self.assertEqual(LogBook.objects.count(), 1)
        self.assertEqual(log.log_user, self.user)
        self.assertEqual(log.log_action, "Performed an action")
        self.assertEqual(log.log_result, "success")

    def test_create_log_with_anonymous_user(self):
        """Test create_log with an anonymous user."""
        create_log(self.anonymous_user, "Anonymous action")
        log = LogBook.objects.first()
        self.assertEqual(LogBook.objects.count(), 1)
        self.assertIsNone(log.log_user)
        self.assertEqual(log.log_action, "Anonymous action")

    def test_create_log_with_none_user(self):
        """Test create_log with None as the user."""
        create_log(None, "System action")
        log = LogBook.objects.first()
        self.assertEqual(LogBook.objects.count(), 1)
        self.assertIsNone(log.log_user)
        self.assertEqual(log.log_action, "System action")

    def test_create_log_with_custom_result(self):
        """Test create_log with a custom result like 'failure'."""
        create_log(self.user, "Failed action", result="failure")
        log = LogBook.objects.first()
        self.assertEqual(log.log_result, "failure")