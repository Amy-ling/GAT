

from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Item
import random
from django.contrib.auth.forms import AuthenticationForm

class MultipleFileInput(forms.ClearableFileInput):
    """
    A custom widget that allows for the selection of multiple files.
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A custom form field that uses the MultipleFileInput widget.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class UserRegisterForm(forms.Form):
    phone = forms.CharField(
        label='Phone Number',
        help_text='Your 8-digit phone number. This will be your login ID in the future.',
        min_length=8,
        max_length=8,
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': '8-digit phone number'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text=' Your password can’t be too similar to your other personal information.<br> Your password must contain at least 8 characters.<br> Your password can’t be a commonly used password.<br> Your password can’t be entirely numeric.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must be digits")

        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number has been registered")

        return int(phone)

    def clean_password2(self):
        cd = self.cleaned_data
        password = cd.get('password')
        password2 = cd.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match.")

        if password:
            try:
                validate_password(password)
            except forms.ValidationError as e:
                self.add_error('password', e)

        return password2

    @transaction.atomic
    def save(self):
        while True:
            random_username = f"User{random.randint(10000, 99999)}"
            if not User.objects.filter(username=random_username).exists():
                break

        user = User.objects.create_user(
            username=random_username,
            password=self.cleaned_data.get('password')
        )

        UserProfile.objects.create(
            user=user,
            phone=self.cleaned_data.get('phone'),
            name=random_username,
            is_admin=False
        )
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Phone Number',
        help_text='Please enter your 8-digit phone number.',
        min_length=8,
        max_length=8,
        widget=forms.TextInput(attrs={'type': 'number', 'placeholder': '8-digit phone number'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isdigit():
            raise forms.ValidationError("Phone number must be digits.")
        return username

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Display Name"
        self.fields['name'].help_text = "This name will be visible to other users."

class ItemForm(forms.ModelForm):
    item_image = MultipleFileField(
        required=False,
        label="Upload Image(s) (Max 6)"
    )

    class Meta:
        model = Item
        fields = ['item_name', 'item_type', 'description', 'item_image']
        labels = {
            'item_name': 'Item Name',
            'item_type': 'Item Type',
            'description': 'Description',
        }

    def clean_item_image(self):
        images = self.files.getlist('item_image')
        if len(images) > 6:
            raise forms.ValidationError("You can only upload up to 6 images.")
        return images