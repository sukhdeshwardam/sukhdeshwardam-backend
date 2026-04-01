from rest_framework import serializers
from .models import Treatment
from cattle.models import Cow


class TreatmentSerializer(serializers.ModelSerializer):
    # --- read-only denormalised fields ---
    cow_token_no = serializers.ReadOnlyField(source='cow.token_no')
    cow_admission_date = serializers.ReadOnlyField(source='cow.admission_date')
    cow_diseases = serializers.ReadOnlyField(source='cow.diseases')
    cow_history = serializers.ReadOnlyField(source='cow.history')
    cow_condition = serializers.ReadOnlyField(source='cow.condition')
    doctor_name = serializers.SerializerMethodField()

    # --- write-only: accept token number as an alternative to cow PK ---
    cow_token_no_input = serializers.CharField(
        write_only=True, required=False, allow_blank=True,
        help_text="Supply this instead of 'cow' to look up the cow by token number."
    )

    class Meta:
        model = Treatment
        fields = '__all__'
        extra_kwargs = {
            # cow FK is not required when cow_token_no_input is provided
            'cow': {'required': False},
        }

    def validate(self, attrs):
        token_input = attrs.pop('cow_token_no_input', None)
        if token_input:
            cow, _ = Cow.objects.get_or_create(
                token_no=token_input,
                defaults={
                    'caller_of_rescue': 'Unknown',
                    'gender': 'Female',
                    'breed': 'Unknown',
                }
            )
            attrs['cow'] = cow
        if 'cow' not in attrs or attrs.get('cow') is None:
            raise serializers.ValidationError(
                {'cow': 'A cow must be specified either by ID or by token number.'}
            )
        return attrs

    def get_doctor_name(self, obj):
        if obj.doctor:
            if obj.doctor.first_name:
                return f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
            return obj.doctor.email
        return "N/A"
