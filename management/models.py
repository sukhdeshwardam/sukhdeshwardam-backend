from django.db import models
from django.conf import settings
from django.utils import timezone

class Visitor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField()
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='visitors')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Donation(models.Model):
    DONATION_CHOICES = [
        ('Money', 'Money'),
        ('Material', 'Material'),
    ]
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_type = models.CharField(max_length=20, choices=DONATION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    material_details = models.TextField(blank=True, null=True)
    material_quantity = models.CharField(max_length=255, blank=True, null=True)
    donation_date = models.DateField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='donations_logged')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.donation_type} on {self.created_at.date()}"
class Visit(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateField()
    visit_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor.name} - {self.visit_date} {self.visit_time}"

    class Meta:
        ordering = ['-visit_date']

class BirthdayWishLog(models.Model):
    """Tracks birthday wishes already sent today to prevent double-charging."""
    phone = models.CharField(max_length=20)
    sent_on = models.DateField()  # The date the wish was sent (today's date)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('phone', 'sent_on')  # One wish per phone per day

    def __str__(self):
        return f"{self.phone} - {self.sent_on}"
