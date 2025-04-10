from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()  # Convert to lowercase
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account was already registered using this email")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()  # Ensure lowercase email
        user.is_active = False  # User will be inactive until approved
        if commit:
            user.save()
        return user