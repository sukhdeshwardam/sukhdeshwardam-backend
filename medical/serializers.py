from rest_framework import serializers
from .models import Treatment

class TreatmentSerializer(serializers.ModelSerializer):
    cow_token_no = serializers.ReadOnlyField(source='cow.token_no')
    cow_admission_date = serializers.ReadOnlyField(source='cow.admission_date')
    cow_diseases = serializers.ReadOnlyField(source='cow.diseases')
    cow_history = serializers.ReadOnlyField(source='cow.history')
    cow_condition = serializers.ReadOnlyField(source='cow.condition')
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = '__all__'

    def get_doctor_name(self, obj):
        if obj.doctor:
            if obj.doctor.first_name:
                return f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
            return obj.doctor.email
        return "N/A"
