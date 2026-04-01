from rest_framework import serializers
from .models import Visitor, Donor, Donation, Visit

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class VisitorSerializer(serializers.ModelSerializer):
    added_by_name = serializers.ReadOnlyField(source='added_by.name')
    visits = VisitSerializer(many=True, read_only=True)
    last_visit_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Visitor
        fields = '__all__'

    def get_last_visit_date(self, obj):
        last = obj.visits.order_by('-visit_date').first()
        return last.visit_date if last else None

class DonationSerializer(serializers.ModelSerializer):
    added_by_name = serializers.ReadOnlyField(source='added_by.name')
    
    class Meta:
        model = Donation
        fields = '__all__'

class DonorSerializer(serializers.ModelSerializer):
    donations = DonationSerializer(many=True, read_only=True)
    total_money = serializers.SerializerMethodField()
    material_summary = serializers.SerializerMethodField()
    last_donation_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Donor
        fields = '__all__'

    def get_total_money(self, obj):
        return sum(d.amount for d in obj.donations.filter(donation_type='Money') if d.amount)

    def get_material_summary(self, obj):
        materials = obj.donations.filter(donation_type='Material')
        if not materials:
            return None
        # Join unique material details
        unique_mats = list(set(m.material_details for m in materials if m.material_details))
        return ", ".join(unique_mats[:2]) + ("..." if len(unique_mats) > 2 else "")

    def get_last_donation_date(self, obj):
        last = obj.donations.order_by('-donation_date').first()
        return last.donation_date if last else None
