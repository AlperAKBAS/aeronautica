from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
# Create your models here.

# https://www.youtube.com/watch?v=HshbjK1vDtY&ab_channel=CodingEntrepreneurs
# Database fixture or Database backup https://youtu.be/HshbjK1vDtY?t=1661

def email_domain_validator(email_value):
    """Validates if email not ending with hotmail.com etc."""
    blacklisted_emails = settings.EMAIL_DOMAIN_BLACKLIST

    email_domain = email_value.split('@')[-1]
    if email_domain in blacklisted_emails:
        raise ValidationError(
        _(f'{email_domain} This domain not supported.'),
        )
  
    return email_value


class UserManager(BaseUserManager):

    def create_user(
        self, email, first_name, last_name, password=None, 
        is_active=True, is_staff=False, is_demo_user=False, is_admin=False, **extrafields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Email is required to create a user.')
        else:
            email = email_domain_validator(email)

        if not first_name:
            raise ValueError('Please provide your firstname.')

        if not last_name:
            raise ValueError('Please provide your surname.')

        user = self.model(
            email=self.normalize_email(email), 
            first_name = first_name,
            last_name = last_name.upper(),
            **extrafields)

        user.is_active = is_active
        user.is_admin = is_admin
        user.is_staff = is_staff
        user.is_demo_user = is_demo_user
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_demo_user(self, email, first_name, last_name, password):
        user = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
            is_demo_user=True,
        )
        return user

    def create_staffuser(self, email, first_name, last_name,password):
        user = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, first_name, last_name, password):   
        """Creates and saves superuser"""
        user = self.create_user(
            email, 
            first_name,
            last_name,
            password, 
            is_staff=True, is_admin=True)
        user.is_superuser = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_demo_user = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email' # we converted to email default
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name.upper()}'




class Profile(models.Model):
    """Profile Inormation for Each User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    title = models.CharField(max_length=25, null=True, blank=True) # Mr. Mrs. Mss. 
    company = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    is_company_admin = models.BooleanField(default=False)
    udpated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=355, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    # mobile_number = models.CharField(max_length=120, blank=True, null=True)

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name.upper()}'

    def __str__(self):
        return f'{self.user.email}'