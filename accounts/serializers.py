from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import CustomUser


# ─────────────────────────────────────────────
# User Serializer (read-only profile data)
# ─────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 'profile_image', 'role', 'is_verified', 'date_joined',
                  'joining_date', 'gender', 'dob', 'specialization', 'qualification', 'experience', 'address')
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url  # Returns full Cloudinary https:// URL
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_image', 'password',
                  'joining_date', 'gender', 'dob', 'specialization', 'qualification', 'experience', 'address')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


# ─────────────────────────────────────────────
# Register Serializer
# ─────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')

    class Meta:
        model  = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'password2')

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active   = False   # locked until OTP verified
        user.is_verified = False
        user.save()
        return user


# ─────────────────────────────────────────────
# OTP Verify Serializer
# ─────────────────────────────────────────────

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code  = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('OTP must be numeric.')
        return value


# ─────────────────────────────────────────────
# Resend OTP Serializer
# ─────────────────────────────────────────────

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ─────────────────────────────────────────────
# Login Serializer
# ─────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# ─────────────────────────────────────────────
# Forgot Password Serializer
# ─────────────────────────────────────────────

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ─────────────────────────────────────────────
# Password Reset Confirm Serializer
# ─────────────────────────────────────────────

class PasswordResetConfirmSerializer(serializers.Serializer):
    email         = serializers.EmailField()
    code          = serializers.CharField(max_length=6, min_length=6)
    new_password  = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, label='Confirm New Password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        return attrs

# ─────────────────────────────────────────────
# User CRUD Serializer (For Admins)
# ─────────────────────────────────────────────

class UserCrudSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image', 'role', 'password', 'is_active', 'is_verified',
                  'joining_date', 'gender', 'dob', 'specialization', 'qualification', 'experience', 'address')
        extra_kwargs = {
            'email': {'validators': []} # Allow unique validator to be handled by ModelSerializer naturally
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        # Auto-verify users created directly by Admin
        user.is_verified = True
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
