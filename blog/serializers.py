from rest_framework import serializers
from .models import BlogPost
from accounts.serializers import UserProfileSerializer

class BlogPostSerializer(serializers.ModelSerializer):
    author_details = UserProfileSerializer(source='author', read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    cover_image = serializers.ImageField(required=False, allow_null=True, use_url=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'author', 'author_details', 'title', 'content', 'cover_image', 'cover_image_url', 'category', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
