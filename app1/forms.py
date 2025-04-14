from django import forms
from django.contrib.auth.hashers import make_password
from .models import Account

class OTPForm(forms.Form):
    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': '6-digit code', 'autocomplete': 'one-time-code', 'inputmode': 'numeric'}) # Improved attributes
    )

class RegForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Enter a strong password.")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Account
        fields = ['username', 'email', 'phone', 'password', 'confirm_password'] # Order matters for display

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            pass
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'})) # Use standard length, add placeholder
    password = forms.CharField(max_length=128, widget=forms.PasswordInput(attrs={'placeholder': 'Password'})) # Use standard length, add placeholder

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'email', 'phone', 'first_name', 'last_name', 'profile_pic'] # Added first/last name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your full shipping address'}), label="Shipping Address")
    billing_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter billing address if different'}), required=False, label="Billing Address (if different)")
    same_as_shipping = forms.BooleanField(
        initial=True, required=False,
        label="Billing address is the same as shipping address",
        widget=forms.CheckboxInput(attrs={'onclick': 'toggleBillingAddress(this)'}) # JS hook
    )