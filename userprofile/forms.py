from django import forms
from django.contrib.auth.models import User
from userprofile.models import UserProfile, Payment


# User Form
class UserForm(forms.ModelForm):

    # make sure password isn't in plaintext
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User

        # only show username, email, and password fields
        fields = ('username', 'email', 'password')


# User Profile Form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

        # only show location and phone number fields
        fields = ('location', 'phone_number')

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('creditcard_number', 'security_code', 'expiration_month', 'expiration_year')