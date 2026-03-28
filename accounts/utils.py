import random
import string
import ssl
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.conf import settings
from django.utils import timezone
from django.utils.functional import cached_property

class SSLBypassEmailBackend(SMTPEmailBackend):
    @cached_property
    def ssl_context(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(user, otp_code: str) -> None:
    subject = 'Gau-Shala – Email Verification OTP'
    message = (
        f'Hello {user.get_full_name() or user.email},\n\n'
        f'Your OTP for email verification is:\n\n'
        f'        {otp_code}\n\n'
        f'Valid for {getattr(settings, "OTP_EXPIRY_MINUTES", 10)} minutes.\n'
        f'Do NOT share it with anyone.\n\n'
        f'Regards,\nGau-Shala Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def send_password_reset_email(user, reset_token: str) -> None:
    subject = 'Gau-Shala – Password Reset Request'
    message = (
        f'Hello {user.get_full_name() or user.email},\n\n'
        f'Use this token to reset your password (POST to /api/auth/reset-password/):\n\n'
        f'  Token: {reset_token}\n\n'
        f'Valid for {getattr(settings, "PASSWORD_RESET_EXPIRY_HOURS", 1)} hour(s).\n'
        f'If you did not request this, ignore this email.\n\n'
        f'Regards,\nGau-Shala Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def create_and_send_otp(user) -> str:
    from accounts.models import OTP
    OTP.objects.filter(user=user, is_used=False).update(is_used=True)
    code = generate_otp()
    OTP.objects.create(user=user, code=code)
    send_otp_email(user, code)
    return code
