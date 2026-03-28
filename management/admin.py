from django.contrib import admin
from .models import Visitor, Donor, Donation

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'added_by', 'created_at')
    search_fields = ('name', 'phone', 'email')

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'donation_type', 'amount', 'added_by', 'created_at')
    list_filter = ('donation_type', 'created_at')
    search_fields = ('donor__name', 'donor__phone')
