from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser, OTP, PasswordResetToken
from accounts.serializers import (
    RegisterSerializer,
    OTPVerifySerializer,
    ResendOTPSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserCrudSerializer,
)
from accounts.utils import create_and_send_otp, send_password_reset_email
from django.db import transaction
from django.db.models import Sum
from medical.models import Treatment
from cattle.models import Cow
from inventory.models import Medicine


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def get_tokens_for_user(user):
    """Return JWT access + refresh tokens for the given user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


def role_check(user, *roles):
    return user.role in roles


# ─────────────────────────────────────────────
# POST /api/auth/register/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def register_view(request):
    """
    Register a new user (admin / doctor / member).
    Sends a 6-digit OTP to the provided email.
    Account is inactive until OTP is verified.

    Request Body:
        email, first_name, last_name, role, password, password2
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        create_and_send_otp(user)
        return Response(
            {
                'message': 'Registration successful. OTP sent to your email. Please verify to activate your account.',
                'email': user.email,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# POST /api/auth/verify-otp/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def otp_verify_view(request):
    """
    Verify the OTP for a registered email.
    On success, activates the account and returns JWT tokens.

    Request Body:
        email, code
    """
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()
    code  = serializer.validated_data['code']

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_verified:
        return Response({'message': 'Account is already verified. Please log in.'}, status=status.HTTP_200_OK)

    otp_obj = OTP.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()

    if otp_obj is None:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    if otp_obj.is_expired():
        return Response({'error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    # Activate user — Members require Admin approval before they can log in
    otp_obj.is_used  = True
    otp_obj.save()
    user.is_verified = True

    if user.role == CustomUser.Role.MEMBER:
        # Keep is_active=False until Admin approves
        user.save(update_fields=['is_verified'])
        return Response(
            {
                'message':         'Email verified successfully! Your account is pending admin approval. You will be able to log in once an admin activates your account.',
                'pending_approval': True,
            },
            status=status.HTTP_200_OK,
        )

    # Admins and Doctors are activated immediately
    user.is_active = True
    user.save(update_fields=['is_active', 'is_verified'])

    tokens = get_tokens_for_user(user)
    return Response(
        {
            'message': 'Email verified successfully. Account activated.',
            'user':    UserProfileSerializer(user).data,
            'tokens':  tokens,
        },
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# POST /api/auth/resend-otp/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp_view(request):
    """
    Resend a fresh OTP to the given email.
    Only allowed for unverified accounts.

    Request Body:
        email
    """
    serializer = ResendOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_verified:
        return Response({'message': 'Account is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

    create_and_send_otp(user)
    return Response({'message': 'A new OTP has been sent to your email.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# POST /api/auth/login/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and return JWT tokens + role info.

    Request Body:
        email, password

    Response:
        access token, refresh token, role, user profile
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email    = serializer.validated_data['email'].lower()
    password = serializer.validated_data['password']

    # Check if user exists but not verified
    try:
        user_check = CustomUser.objects.get(email=email)
        if not user_check.is_verified:
            return Response(
                {'error': 'Account not verified. Please check your email for the OTP.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Verified member but not yet approved by admin
        if user_check.is_verified and not user_check.is_active and user_check.role == CustomUser.Role.MEMBER:
            return Response(
                {'error': 'Your account is pending admin approval. Please wait for an administrator to activate your account.'},
                status=status.HTTP_403_FORBIDDEN,
            )
    except CustomUser.DoesNotExist:
        pass

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = get_tokens_for_user(user)
    return Response(
        {
            'message': f'Login successful.',
            'role':    user.role,
            'user':    UserProfileSerializer(user).data,
            'tokens':  tokens,
        },
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# POST /api/auth/logout/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Blacklist the refresh token to log out.

    Request Body:
        refresh  (the refresh token string)
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# POST /api/auth/forgot-password/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Send a 6-digit OTP to the user's email for password reset.
    Always returns success to prevent user enumeration.

    Request Body:
        email
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()

    try:
        user = CustomUser.objects.get(email=email)
        create_and_send_otp(user)
    except CustomUser.DoesNotExist:
        pass  # Silently ignore to avoid enumeration

    return Response(
        {'message': 'If that email is registered, an OTP will be sent.'},
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# POST /api/auth/reset-password/
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Reset the user's password using the 6-digit OTP from the email.

    Request Body:
        email, code, new_password, new_password2
    """
    from accounts.models import OTP

    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()
    code  = serializer.validated_data['code']

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTP.objects.filter(user=user, code=code, is_used=False).order_by('-created_at').first()

    if otp_obj is None:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    if otp_obj.is_expired():
        return Response({'error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    # Valid OTP, update password
    user.set_password(serializer.validated_data['new_password'])
    user.save()

    otp_obj.is_used = True
    otp_obj.save()

    return Response({'message': 'Password reset successful. You can now log in.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# GET /api/auth/profile/
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Return the authenticated user's profile.
    Accessible to all roles (admin, doctor, member).
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────
# GET /api/auth/dashboard/admin/
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_view(request):
    """Admin-only endpoint."""
    if not role_check(request.user, CustomUser.Role.ADMIN):
        return Response({'error': 'Access denied. Admin role required.'}, status=status.HTTP_403_FORBIDDEN)

    users = CustomUser.objects.all().order_by('-date_joined')[:10]
    return Response(
        {
            'message':       'Admin Dashboard',
            'total_users':   CustomUser.objects.count(),
            'total_doctors': CustomUser.objects.filter(role=CustomUser.Role.DOCTOR).count(),
            'total_members': CustomUser.objects.filter(role=CustomUser.Role.MEMBER).count(),
            'recent_users':  UserProfileSerializer(users, many=True).data,
        },
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# GET /api/auth/dashboard/doctor/
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_dashboard_view(request):
    """Doctor-only endpoint."""
    if not role_check(request.user, CustomUser.Role.DOCTOR):
        return Response({'error': 'Access denied. Doctor role required.'}, status=status.HTTP_403_FORBIDDEN)

    # Count unique cows whose latest status is 'Death'
    total_deaths = Treatment.objects.order_by('cow', '-checkup_date').distinct('cow').filter(status='Death').count()
    total_cows = Cow.objects.count()
    total_medicines_stock = Medicine.objects.aggregate(total=Sum('stock'))['total'] or 0

    return Response(
        {
            'message': 'Doctor Dashboard',
            'user':    UserProfileSerializer(request.user).data,
            'stats': {
                'total_deaths': total_deaths,
                'total_cows': total_cows,
                'total_medicines_stock': total_medicines_stock,
            }
        },
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# GET /api/auth/dashboard/member/
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_dashboard_view(request):
    """Member-only endpoint."""
    if not role_check(request.user, CustomUser.Role.MEMBER):
        return Response({'error': 'Access denied. Member role required.'}, status=status.HTTP_403_FORBIDDEN)

    return Response(
        {
            'message': 'Member Dashboard',
            'user':    UserProfileSerializer(request.user).data,
        },
        status=status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# PATCH /api/auth/profile/update/
# ─────────────────────────────────────────────

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def profile_update_view(request):
    """
    Update the authenticated user's profile.
    Supports partial updates for first_name, last_name, email, phone_number, profile_image, and password.
    """
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'message': 'Profile updated successfully.',
                'user': UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ─────────────────────────────────────────────
# VIEWSET /api/auth/users/ (Admin Only)
# ─────────────────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Users.
    Strictly restricted to Admin role.
    Supports filtering via query parameter: `?role=doctor`
    """
    serializer_class = UserCrudSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not role_check(self.request.user, CustomUser.Role.ADMIN):
            return CustomUser.objects.none()
            
        queryset = CustomUser.objects.all().order_by('-date_joined')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def check_permissions(self, request):
        super().check_permissions(request)
        if not role_check(request.user, CustomUser.Role.ADMIN):
            self.permission_denied(request, message="Access denied. Admin role required.")
