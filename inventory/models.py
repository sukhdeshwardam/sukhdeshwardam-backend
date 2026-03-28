from django.db import models
from django.utils import timezone

class Medicine(models.Model):
    medicine_name = models.CharField(max_length=150, default="Unknown Medicine")
    number = models.CharField(max_length=50, help_text="Medicine ID or Batch Number")
    stock = models.PositiveIntegerField(default=0, help_text="Current stock quantity")
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
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
    quantity = models.PositiveIntegerField()
    usage_date = models.DateTimeField(default=timezone.now)
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='Used')
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            # Handle quantity change on update
            old_record = MedicineUsage.objects.get(pk=self.pk)
            diff = self.quantity - old_record.quantity
            self.medicine.stock -= diff
        else:
            # Handle new record
            self.medicine.stock -= self.quantity
        
        # Ensure stock doesn't go below zero if possible (though we'll allow it if needed, but PositiveIntegerField will complain)
        self.medicine.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Restore stock if record is deleted
        self.medicine.stock += self.quantity
        self.medicine.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.usage_type}: {self.medicine.medicine_name} ({self.quantity})"

    class Meta:
        ordering = ['-usage_date']
        verbose_name_plural = "Medicine Usages"
