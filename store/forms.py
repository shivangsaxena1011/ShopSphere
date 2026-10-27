from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from store.models import UserProfile

class UserRegisterForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Enter your full name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Create a secure password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")

        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Email or Username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(required=False, initial=True)


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'e.g. Shivang Saxena'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': '+91 98765 43210'
        })
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Flat / House No., Street, Landmark'
        })
    )
    city = forms.CharField(
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'e.g. Bhopal'
        })
    )
    state = forms.CharField(
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'e.g. Madhya Pradesh'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'e.g. 462001'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-lowest border border-outline-variant focus:border-primary rounded-lg px-4 py-3 text-on-surface text-body-md focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all',
            'placeholder': 'Optional delivery instructions (e.g., ring doorbell)'
        })
    )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'postal_code']
