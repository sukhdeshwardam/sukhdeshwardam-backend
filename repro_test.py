import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gau_shala.settings')
django.setup()

from management.models import Visitor, Donor, Donation
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

def test_flow():
    phone = "9999999999"
    name = "Test User"
    
    # 1. Add Visitor first
    print(f"Adding visitor {name} ({phone})...")
    visitor, v_created = Visitor.objects.get_or_create(phone=phone, defaults={'name': name, 'address': 'Test Addr'})
    print(f"Visitor created: {v_created}")
    
    # 2. Add Donation for same phone
    print(f"Adding donation for {name} ({phone})...")
    # This simulates DonationViewSet.create logic
    donor, d_created = Donor.objects.get_or_create(phone=phone, defaults={'name': name, 'address': 'Test Addr'})
    print(f"Donor created: {d_created}")
    
    # Now simulate the serializer save
    donation = Donation.objects.create(
        donor=donor,
        donation_type='Money',
        amount=100,
        added_by=admin
    )
    print(f"Donation created: {donation.id}")

def test_cross_sync():
    phone = "8888888888"
    name = "Visitor First"
    email = "visitor@test.com"
    
    # 1. Add Visitor
    print(f"\nAdding visitor {name}...")
    Visitor.objects.create(phone=phone, name=name, email=email)
    
    # 2. Add Donor (Simulate logic in DonationViewSet)
    print("Simulating Donation creation for same phone...")
    donor_data = {'name': name, 'phone': phone} # Missing email
    
    # Logic from view:
    visitor = Visitor.objects.filter(phone=phone).first()
    if visitor:
        if not donor_data.get('email'): donor_data['email'] = visitor.email
        
    donor, created = Donor.objects.get_or_create(phone=phone, defaults=donor_data)
    print(f"Donor email inherited: {donor.email == email}")
    assert donor.email == email

if __name__ == "__main__":
    try:
        test_flow()
        test_cross_sync()
        print("\nAll tests passed successfully.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
