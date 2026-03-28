from django.contrib import admin
from .models import Medicine, CowFoodStock, MedicineUsage

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'number', 'stock', 'expiry_date', 'store_phone_number', 'bill_number', 'stia_name')
    search_fields = ('medicine_name', 'number', 'bill_number', 'stia_name')
    list_filter = ('date_time', 'expiry_date')

@admin.register(CowFoodStock)
class CowFoodStockAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'quantity_kg', 'supplier', 'purchase_date')
    search_fields = ('food_name', 'supplier')
    list_filter = ('purchase_date',)

@admin.register(MedicineUsage)
class MedicineUsageAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'quantity', 'usage_type', 'usage_date')
    list_filter = ('usage_type', 'usage_date')
    search_fields = ('medicine__medicine_name', 'medicine__number')
