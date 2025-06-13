
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from .models import UserProfile, Item
import random
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# You can remove the UserLoginForm if you are not using it yet, or keep it for later.

class UserRegisterForm(forms.Form):
    # We only define the fields the user needs to see.
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
        """
        Validate that the phone number is unique.
        """
        phone = self.cleaned_data.get('phone')
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone

    def clean_password2(self):
        """
        Validate that the two password fields match.
        """
        cd = self.cleaned_data
        if cd.get('password') and cd.get('password2') and cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd.get('password2')

    @transaction.atomic
    def save(self):
        """
        This method handles creating the User and UserProfile objects.
        """
        # Generate a unique random username
        while True:
            # Example: "User" + a 5-digit random number
            random_username = f"User{random.randint(10000, 99999)}"
            if not User.objects.filter(username=random_username).exists():
                break # Break the loop if the username is unique

        # Create the main User object
        user = User.objects.create_user(
            username=random_username,
            password=self.cleaned_data.get('password')
        )

        # Create the associated UserProfile
        profile = UserProfile.objects.create(
            user=user,
            phone=self.cleaned_data.get('phone'),
            # Use the random username as the initial display name
            name=random_username
        )

        return user

class UserLoginForm(AuthenticationForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Change the label for the 'username' field
            self.fields['username'].label = 'Phone Number'
            self.fields['username'].help_text = 'Enter the 8-digit phone number you registered with.'

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # List the fields from your UserProfile model that the user can edit.
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize field labels or help text if you want
        self.fields['name'].label = "Display Name"
        self.fields['name'].help_text = "This name will be visible to other users."

class ItemForm(forms.ModelForm):
    item_image = forms.ImageField(required=False, label="Upload Image")

    class Meta:
        model = Item
        fields = ['item_name', 'item_type', 'description', 'item_image']
        labels = {
            'item_name': '物品名稱',
            'item_type': '物品類型',
            'description': '物品描述',
        }