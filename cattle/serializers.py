from rest_framework import serializers
from .models import Cow, CowBaseStats

class CowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cow
        fields = '__all__'

class CowBaseStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CowBaseStats
        fields = '__all__'
