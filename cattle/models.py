from django.db import models
from django.utils import timezone

class Cow(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    CATEGORY_CHOICES = [
        ('Cow', 'Cow'),
        ('Bull', 'Bull'),
        ('Calf', 'Calf'),
        ('Heifer', 'Heifer'),
        ('Nandi', 'Nandi'),
    ]
    

    caller_of_rescue = models.CharField(max_length=100)
    caller_of_rescue_number = models.CharField(max_length=20, blank=True, null=True)
    rescuer_name   = models.CharField(max_length=100, blank=True, null=True)
    gender         = models.CharField(max_length=10, choices=GENDER_CHOICES)
    breed          = models.CharField(max_length=100)
    token_no       = models.CharField(max_length=50, unique=True)
    place_of_rescue = models.TextField(blank=True, null=True)
    admission_date = models.DateField(default=timezone.now)
    diseases       = models.TextField(blank=True, null=True, help_text="Comma-separated list of diseases or detailed description.")
    symptoms       = models.TextField(blank=True, null=True)
    history        = models.TextField(blank=True, null=True)
    mode_of_transport = models.CharField(max_length=100, blank=True, null=True)
    colour         = models.CharField(max_length=100, blank=True, null=True)
    other_details  = models.TextField(blank=True, null=True)

    
    CONDITION_CHOICES = [
        ('Normal', 'Normal'),
        ('Serious', 'Serious'),
    ]
    condition      = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Normal')
    category       = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Cow')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.token_no} - {self.caller_of_rescue} ({self.breed})"

    class Meta:
        ordering = ['-admission_date', '-created_at']

class CowBaseStats(models.Model):
    total = models.IntegerField(default=296)
    cows = models.IntegerField(default=0)
    bulls = models.IntegerField(default=0)
    female_calves = models.IntegerField(default=33)
    male_calves = models.IntegerField(default=95)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name_plural = "Cow Base Stats"
