import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings

from cloudinary.models import CloudinaryField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN  = 'admin',  'Admin'
        DOCTOR = 'doctor', 'Doctor'
        MEMBER = 'member', 'Member'

    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=150)
    last_name   = models.CharField(max_length=150, blank=True)
    role         = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = CloudinaryField('image', null=True, blank=True)
    is_active    = models.BooleanField(default=False)   # activated after OTP
    is_staff    = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)   # email verified
    date_joined = models.DateTimeField(default=timezone.now)

    # Added profile fields
    joining_date = models.DateField(null=True, blank=True)
    gender       = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    dob          = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    specialization = models.CharField(max_length=255, blank=True)
    qualification  = models.CharField(max_length=255, blank=True)
    experience     = models.CharField(max_length=100, blank=True)
    address        = models.TextField(blank=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = CustomUserManager()

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class OTP(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP({self.user.email}, used={self.is_used})'

    def is_expired(self):
        expiry = self.created_at + timezone.timedelta(
            minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        )
        return timezone.now() > expiry

    def is_valid(self):
        return not self.is_used and not self.is_expired()


class PasswordResetToken(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reset_tokens')
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'ResetToken({self.user.email}, used={self.is_used})'

    def is_expired(self):
        expiry = self.created_at + timezone.timedelta(
            hours=getattr(settings, 'PASSWORD_RESET_EXPIRY_HOURS', 1)
        )
        return timezone.now() > expiry

    def is_valid(self):
        return not self.is_used and not self.is_expired()
