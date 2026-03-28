from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class BlogPost(models.Model):
    class Category(models.TextChoices):
        COWS = 'Cows', 'Cows'
        FEEDING = 'Feeding', 'Feeding'
        MEDICAL = 'Medical', 'Medical'
        EVENTS = 'Events', 'Events'
        VOLUNTEERS = 'Volunteers', 'Volunteers'
        GENERAL = 'General', 'General'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    cover_image = CloudinaryField('image', null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
