from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import CustomUser, OTP, PasswordResetToken


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display     = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_verified', 'date_joined')
    list_filter      = ('role', 'is_active', 'is_verified', 'is_staff')
    search_fields    = ('email', 'first_name', 'last_name')
    ordering         = ('-date_joined',)
    readonly_fields  = ('date_joined', 'last_login')

    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions',   {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Dates',         {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display    = ('user', 'code', 'created_at', 'is_used')
    list_filter     = ('is_used',)
    search_fields   = ('user__email',)
    readonly_fields = ('created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display    = ('user', 'token', 'created_at', 'is_used')
    list_filter     = ('is_used',)
    search_fields   = ('user__email',)
    readonly_fields = ('token', 'created_at')
