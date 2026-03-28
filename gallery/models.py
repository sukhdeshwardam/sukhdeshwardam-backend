from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class GalleryImage(models.Model):
    class Category(models.TextChoices):
        COWS = 'Cows', 'Cows'
        FEEDING = 'Feeding', 'Feeding'
        MEDICAL = 'Medical', 'Medical'
        EVENTS = 'Events', 'Events'
        VOLUNTEERS = 'Volunteers', 'Volunteers'

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gallery_images')
    image = CloudinaryField('image')
    title = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.COWS)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title or 'Gallery Image'} - {self.category}"
