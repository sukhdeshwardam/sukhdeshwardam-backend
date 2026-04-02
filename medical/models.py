from django.db import models
from django.conf import settings
from cattle.models import Cow

class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Treatment(models.Model):
    STATUS_CHOICES = [
        ('Ongoing', 'Ongoing'),
        ('Recovered', 'Recovered'),
    ]

    cow = models.ForeignKey(Cow, on_delete=models.CASCADE, related_name='treatments')
    checkup_date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField()
    medicine = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Update Cow medical history
            cow = self.cow
            date_str = self.checkup_date.strftime('%Y-%m-%d %H:%M') if self.checkup_date else '-'
            entry = f"[{date_str}] Symptoms: {self.symptoms} | Medicines: {self.medicine}\n"
            if cow.history:
                cow.history = entry + cow.history
            else:
                cow.history = entry
            cow.save(update_fields=['history'])

    def __str__(self):
        return f"Treatment for {self.cow.token_no} on {self.checkup_date.date() if self.checkup_date else 'N/A'}"

    class Meta:
        ordering = ['-checkup_date']
