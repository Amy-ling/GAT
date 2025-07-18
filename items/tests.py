from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Item, ItemTaken, ItemImage
from .forms import ItemForm, MultipleFileField

class ItemModelTest(TestCase):
    """Test suite for the Item model."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.item = Item.objects.create(
            item_name="Test Item", item_type="Test Type",
            description="A description for the test item.",
            give_user=self.user, item_state="available"
        )

    def test_item_creation(self):
        """Test basic item creation."""
        self.assertEqual(self.item.item_name, "Test Item")
        self.assertEqual(self.item.item_type, "Test Type")
        self.assertEqual(self.item.give_user, self.user)
        self.assertEqual(str(self.item), "Test Item")

    def test_item_name_max_length(self):
        """Test the max_length constraint of item_name."""
        max_length = Item._meta.get_field('item_name').max_length
        item = Item(item_name='a' * (max_length + 1), item_type="Test", give_user=self.user)
        with self.assertRaises(Exception):
            item.full_clean()


class ItemTakenModelTest(TestCase):
    """Test suite for the ItemTaken model."""
    def setUp(self):
        self.giver = User.objects.create_user(username='giver', password='password123')
        self.taker = User.objects.create_user(username='taker', password='password123')
        self.item = Item.objects.create(item_name="Taken Item", item_type="Test Type", give_user=self.giver)
        self.item_taken = ItemTaken.objects.create(item_id=self.item, take_user=self.taker)

    def test_item_taken_creation(self):
        """Test the relationship between Item and ItemTaken."""
        self.assertEqual(self.item_taken.item_id, self.item)
        self.assertEqual(self.item_taken.take_user, self.taker)
        self.assertEqual(str(self.item_taken), "Taken Item")


class ItemImageModelTest(TestCase):
    """Test suite for the ItemImage model."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.item = Item.objects.create(item_name="Item With Image", item_type="Test Type", give_user=self.user)
        # Create a dummy file for the image field
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.item_image = ItemImage.objects.create(item_id=self.item, item_image=self.image)

    def test_item_image_creation(self):
        """Test ItemImage creation and its relationship with Item."""
        self.assertEqual(self.item_image.item_id, self.item)
        self.assertTrue(self.item_image.item_image.name.startswith('item_image/test_image'))
        self.assertEqual(str(self.item_image), "Item With Image")


class ItemViewsTest(TestCase):
    """Test suite for the views in the items app."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.item = Item.objects.create(
            item_name="Test Item", item_type="Test Type",
            give_user=self.user, item_state="available"
        )
        self.taken_item = Item.objects.create(
            item_name="Taken Item", item_type="Test Type",
            give_user=self.user, item_state="taken"
        )

    def test_user_main_view(self):
        """Test the main page for logged-in and anonymous users."""
        response = self.client.get(reverse('items:user_main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.item_name)
        self.assertNotContains(response, self.taken_item.item_name)

    def test_my_history_view_requires_login(self):
        """Test that the history view requires a user to be logged in."""
        response = self.client.get(reverse('items:my_history'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('items:my_history')}")

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('items:my_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.item_name)

    @patch('items.views.create_log')
    def test_give_item_view(self, mock_create_log):
        """Test creating an item via the give_item view."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('items:give_item'))
        self.assertEqual(response.status_code, 200)
        
        post_data = {'item_name': 'New Item', 'item_type': 'OT', 'description': 'A new gadget.'}
        response = self.client.post(reverse('items:give_item'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('items:my_history'))
        self.assertTrue(Item.objects.filter(item_name='New Item').exists())
        mock_create_log.assert_called()

    @patch('items.views.create_log')
    def test_take_item_view(self, mock_create_log):
        """Test taking an item."""
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(reverse('items:take_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.item_state, 'taken')
        self.assertTrue(ItemTaken.objects.filter(item_id=self.item, take_user=self.other_user).exists())
        mock_create_log.assert_called()

    def test_user_cannot_take_own_item(self):
        """Test that a user cannot take their own item."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('items:take_item', args=[self.item.id]))
        # The view redirects, so we check the final destination
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('items:user_main'))

    @patch('items.views.create_log')
    def test_edit_item_view(self, mock_create_log):
        """Test editing an item."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('items:edit_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)

        post_data = {'item_name': 'Edited Item', 'item_type': 'OT', 'description': 'Updated description.'}
        response = self.client.post(reverse('items:edit_item', args=[self.item.id]), post_data)
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.item_name, 'Edited Item')
        mock_create_log.assert_called()

    def test_user_cannot_edit_others_item(self):
        """Test that a user cannot edit an item they don't own."""
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('items:edit_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 404) # Should be a 404

    @patch('items.views.create_log')
    def test_delete_item_view(self, mock_create_log):
        """Test deleting an item."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('items:delete_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('items:delete_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())
        mock_create_log.assert_called()

    def test_user_cannot_delete_others_item(self):
        """Test that a user cannot delete an item they don't own."""
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('items:delete_item', args=[self.item.id]))
        self.assertEqual(response.status_code, 404) # Should be a 404


class ItemFormTest(TestCase):
    """Test suite for the ItemForm."""

    def test_form_is_valid(self):
        """Test that the form is valid with correct data."""
        form_data = {'item_name': 'A Valid Item', 'item_type': 'OT', 'description': 'A description.'}
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_invalid_missing_required(self):
        """Test that the form is invalid when required fields are missing."""
        form_data = {'item_name': ''} # Missing item_type
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('item_name', form.errors)
        self.assertIn('item_type', form.errors)

    def test_image_upload_count_validation_fail(self):
        """Test validation fails when more than 6 images are uploaded."""
        from django.http import QueryDict
        from django.utils.datastructures import MultiValueDict
        files = [
            SimpleUploadedFile(f"file{i}.jpg", b"content", "image/jpeg")
            for i in range(7)
        ]
        file_dict = MultiValueDict({'item_image': files})
        form_data = {'item_name': 'Too many images', 'item_type': 'Test'}
        form = ItemForm(form_data, file_dict)
        self.assertFalse(form.is_valid())
        self.assertIn('item_image', form.errors)
        self.assertEqual(form.errors['item_image'][0], "You can only upload up to 6 images.")

    def test_image_upload_count_validation_pass(self):
        """Test validation passes with 6 or fewer images."""
        from django.http import QueryDict
        from django.utils.datastructures import MultiValueDict
        files = [
            SimpleUploadedFile(f"file{i}.jpg", b"content", "image/jpeg")
            for i in range(6)
        ]
        file_dict = MultiValueDict({'item_image': files})
        form_data = {'item_name': 'Correct image count', 'item_type': 'OT'}
        form = ItemForm(form_data, file_dict)
        self.assertTrue(form.is_valid())

class MultipleFileFieldTest(TestCase):
    """Test suite for the MultipleFileField."""

    def test_clean_single_file(self):
        """Test that the field can handle a single file."""
        field = MultipleFileField()
        file = SimpleUploadedFile("single.jpg", b"content")
        cleaned_data = field.clean(file)
        self.assertEqual(cleaned_data, file)

    def test_clean_multiple_files(self):
        """Test that the field can handle a list of files."""
        field = MultipleFileField()
        files = [
            SimpleUploadedFile("multi1.jpg", b"content1"),
            SimpleUploadedFile("multi2.jpg", b"content2")
        ]
        cleaned_data = field.clean(files)
        self.assertEqual(cleaned_data, files)
