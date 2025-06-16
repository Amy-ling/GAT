

from django import forms
from django.db import transaction
from django.contrib.auth.models import User
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
    # ... (rest of the form is unchanged) ...
    phone = forms.IntegerField(
        label='Phone Number',
        help_text='Your 8-digit phone number. This will be your login ID in the future.'
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Your password must contain at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') and cd.get('password2') and cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd.get('password2')

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
        profile = UserProfile.objects.create(
            user=user,
            phone=self.cleaned_data.get('phone'),
            name=random_username
        )
        return user

class UserLoginForm(AuthenticationForm):
    # ... (unchanged) ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Phone Number'
        self.fields['username'].help_text = 'Enter the 8-digit phone number you registered with.'

class UserProfileUpdateForm(forms.ModelForm):
    # ... (unchanged) ...
    class Meta:
        model = UserProfile
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Display Name"
        self.fields['name'].help_text = "This name will be visible to other users."


class ItemForm(forms.ModelForm):
    # Use the new custom MultipleFileField for the item images
    item_image = MultipleFileField(
        required=False,
        label="上傳圖片 (可選擇多張)"
    )

    class Meta:
        model = Item
        fields = ['item_name', 'item_type', 'description']
        labels = {
            'item_name': '物品名稱',
            'item_type': '物品類型',
            'description': '物品描述',
        }