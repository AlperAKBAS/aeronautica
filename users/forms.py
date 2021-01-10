## USER VIEWS
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from core.models import Profile
from django.conf import settings

User = get_user_model()

# HELPER FUNCTIONS
def check_email_providers(email_address):
    banned_hosts = settings.EMAIL_DOMAIN_BLACKLIST
    for address in banned_hosts:
        if address in email_address:
            raise forms.ValidationError(f'Currently we cannot accept {address} emails. please try another email')

#FORMS START HERE
class UserRegisterForm(UserCreationForm):
    """Create a new user on browser"""
    email = forms.EmailField(
            required=True,
            validators=[check_email_providers],
        )

    verify_email = forms.EmailField(
        label='Please verify your email',
    )

    class Meta:
        model = User
  
        fields = ['first_name', 'last_name', 'password1', 'password2', 'email']

    def clean(self):
        """Cleaning all in one method
        """
        all_cleaned_data = super().clean()
        email = all_cleaned_data.get('email')
        vemail = all_cleaned_data.get('verify_email')

        if email != vemail:
            raise forms.ValidationError('Your emails must match.')


class UserUpdateForm(forms.ModelForm):

    """User Info Update Form only first_name, last_name"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name']



class ProfileRegisterForm(forms.ModelForm):
    """Update the profile / merged with UserRegisterForm at the frontend. 
        Signals creates profiles"""

    TITLE_CHOICES = [('mr.', 'Mr.'), ('mrs.', 'Mrs.'), ('ms.', 'Ms.')]
    title = forms.ChoiceField(widget=forms.Select, choices=TITLE_CHOICES)
    company = forms.CharField(required=True)
    position = forms.CharField(required=True)
    country = forms.CharField(required=True)
    city = forms.CharField(required=True)

    class Meta:
        model = Profile
        fields = ['title', 'company', 'position', 'country', 'city']