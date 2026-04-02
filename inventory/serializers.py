from rest_framework import serializers
from .models import Medicine, CowFoodStock, MedicineUsage, MedicalStore

class MedicalStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalStore
        fields = '__all__'

class MedicineUsageSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source='medicine.medicine_name')
    batch_number = serializers.ReadOnlyField(source='medicine.number')
    medicine_type = serializers.ReadOnlyField(source='medicine.medicine_type')
    medicine_unit = serializers.ReadOnlyField(source='medicine.medicine_unit')

    class Meta:
        model = MedicineUsage
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    usages = MedicineUsageSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        # Convert empty expiry_date string to None before DateField validation
        if isinstance(data, dict) and data.get('expiry_date') == '':
            data = data.copy()
            data['expiry_date'] = None
        return super().to_internal_value(data)

    class Meta:
        model = Medicine
        fields = '__all__'


class CowFoodStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = CowFoodStock
        fields = '__all__'
