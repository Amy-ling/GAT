from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from users.models import UserProfile
import random
from django.contrib.auth.forms import AuthenticationForm
from logs.services import create_log
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

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

        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Phone number has been registered")

        return phone

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
        phone = self.cleaned_data.get('phone')
        password = self.cleaned_data.get('password')
        user = User.objects.create_user(
            username=phone,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            phone=phone,
            name=phone,
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

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if self.user_cache is None:
            try:
                user = get_user_model()._default_manager.get(username=username)
                if not user.check_password(password):
                    create_log(user, "Login failed: incorrect password", "failure")
            except get_user_model().DoesNotExist:
                create_log(None, f"Login failed: user '{username}' not found", "failure")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isdigit():
            raise forms.ValidationError("Phone number must be digits.")
        return username

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Display Name"
        self.fields['name'].help_text = "This name will be visible to other users."
        self.fields['phone'].label = "Phone Number"
        self.fields['phone'].help_text = "Your 8-digit phone number. This will be your login ID."

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 8:
            raise forms.ValidationError("Phone number must be an 8-digit number.")
        
        # Check if the phone number is already used by another user
        if User.objects.filter(username=phone).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("This phone number is already registered by another user.")
        return phone

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Display Name"
        self.fields['name'].help_text = "This name will be visible to other users."
        self.fields['phone'].label = "Phone Number"
        self.fields['phone'].help_text = "Your 8-digit phone number. This will be your login ID."

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 8:
            raise forms.ValidationError("Phone number must be an 8-digit number.")
        
        # Check if the phone number is already used by another user
        if User.objects.filter(username=phone).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("This phone number is already registered by another user.")
        return phone

class AdminPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].help_text = '<br>Enter the same password as before, for verification.'
