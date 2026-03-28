from rest_framework import serializers
from .models import GalleryImage
from accounts.serializers import UserProfileSerializer

class GalleryImageSerializer(serializers.ModelSerializer):
    uploaded_by_details = UserProfileSerializer(source='uploaded_by', read_only=True)
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'uploaded_by', 'uploaded_by_details', 'image', 'image_url', 'title', 'category', 'is_approved', 'created_at']
        read_only_fields = ['uploaded_by', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
