from django.db import models
from django.utils import timezone

class Medicine(models.Model):
    MEDICINE_TYPE_CHOICES = [
        ('Bottle', 'Bottle'),
        ('Tablets', 'Tablets'),
        ('Injection', 'Injection'),
    ]

    medicine_name = models.CharField(max_length=150, default="Unknown Medicine")
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPE_CHOICES, default='Injection')
    medicine_quantity = models.CharField(max_length=50, blank=True, null=True, help_text="Quantity value for bottle (e.g. 500)")
    medicine_unit = models.CharField(max_length=10, choices=[('ml', 'ml'), ('L', 'L'), ('Units', 'Units')], default='Units')
    number = models.CharField(max_length=50, blank=True, default="", help_text="Medicine ID or Batch Number")
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Current stock quantity (bottles/tablets/etc.)")
    expiry_date = models.DateField(blank=True, null=True, help_text="Expiry date of the medicine")
    store_phone_number = models.CharField(max_length=100, blank=True, null=True, help_text="Phone number of the store")
    date_time = models.DateTimeField(help_text="Date and time of purchase/entry")
    bill_number = models.CharField(max_length=100)
    stia_name = models.CharField(max_length=150, help_text="Staff or Store name")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.number}) - {self.bill_number}"

    class Meta:
        ordering = ['-date_time']
        verbose_name_plural = "Medicines"


class CowFoodStock(models.Model):
    food_name    = models.CharField(max_length=150, help_text="Name of food/fodder (e.g., Hay, Silage, Wheat Bran)")
    quantity_kg  = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in kilograms")
    supplier     = models.CharField(max_length=150, blank=True, help_text="Supplier or vendor name")
    bill_number  = models.CharField(max_length=100, blank=True, null=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_date = models.DateField(help_text="Date of stock purchase")
    notes        = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_name} - {self.quantity_kg}kg"

    class Meta:
        ordering = ['-purchase_date']
        verbose_name_plural = "Cow Food Stocks"


class MedicineUsage(models.Model):
    USAGE_TYPES = [
        ('Used', 'Used'),
        ('Defect', 'Defect'),
        ('Expired', 'Expired'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='usages')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, help_text="Usage quantity (ml for bottles, units for others)")
    usage_date = models.DateTimeField(default=timezone.now)
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='Used')
    notes = models.TextField(blank=True, null=True)

    def get_reduction_amount(self):
        """Calculate how much to reduce from medicine.stock (which is in bottles/units)."""
        if self.medicine.medicine_type == 'Bottle':
            try:
                # Extract numeric value from medicine_quantity (e.g., "500" from "500ml")
                import re
                match = re.search(r"(\d+(\.\d+)?)", str(self.medicine.medicine_quantity))
                if not match:
                    return self.quantity # Fallback to 1:1 if no number found
                
                bottle_size = float(match.group(1))
                if bottle_size <= 0:
                    return self.quantity
                
                # Handle unit conversion if medicine_unit is 'L' (1L = 1000ml)
                # Usage is assumed to be in ml for bottles
                factor = 1000.0 if self.medicine.medicine_unit == 'L' else 1.0
                total_ml_per_bottle = bottle_size * factor
                
                from decimal import Decimal
                return Decimal(str(float(self.quantity) / total_ml_per_bottle))
            except (ValueError, TypeError, ZeroDivisionError):
                return self.quantity
        return self.quantity

    def save(self, *args, **kwargs):
        reduction = self.get_reduction_amount()
        if self.pk:
            # Handle quantity change on update
            old_record = MedicineUsage.objects.get(pk=self.pk)
            old_reduction = old_record.get_reduction_amount()
            diff = reduction - old_reduction
            self.medicine.stock -= diff
        else:
            # Handle new record
            self.medicine.stock -= reduction
        
        self.medicine.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Restore stock if record is deleted
        reduction = self.get_reduction_amount()
        self.medicine.stock += reduction
        self.medicine.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.usage_type}: {self.medicine.medicine_name} ({self.quantity})"

    class Meta:
        ordering = ['-usage_date']
        verbose_name_plural = "Medicine Usages"
