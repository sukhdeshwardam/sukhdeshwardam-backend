from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
    # ── Registration & OTP ──────────────────────────────
    path('register/',    views.register_view,   name='register'),
    path('verify-otp/',  views.otp_verify_view, name='otp_verify'),
    path('resend-otp/',  views.resend_otp_view, name='resend_otp'),

    # ── Login / Logout ───────────────────────────────────
    path('login/',       views.login_view,      name='login'),
    path('logout/',      views.logout_view,     name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ── Password ─────────────────────────────────────────
    path('forgot-password/',  views.forgot_password_view,         name='forgot_password'),
    path('reset-password/',   views.password_reset_confirm_view,  name='password_reset_confirm'),

    # ── Profile ──────────────────────────────────────────
    path('profile/',          views.profile_view,           name='profile'),
    path('profile/update/',    views.profile_update_view,    name='profile_update'),

    # ── Role Dashboards ───────────────────────────────────
    path('dashboard/admin/',   views.admin_dashboard_view,  name='admin_dashboard'),
    path('dashboard/doctor/',  views.doctor_dashboard_view, name='doctor_dashboard'),
    path('dashboard/member/',  views.member_dashboard_view, name='member_dashboard'),
]
