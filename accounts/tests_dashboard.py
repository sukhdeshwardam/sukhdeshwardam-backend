from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from cattle.models import Cow
from medical.models import Treatment
from inventory.models import Medicine

class DoctorDashboardTests(APITestCase):
    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            email='doctor@example.com',
            password='password123',
            first_name='Doctor',
            last_name='Who',
            role=CustomUser.Role.DOCTOR
        )
        self.client.force_authenticate(user=self.doctor)
        
        # Create some data for stats
        Cow.objects.create(name='Cow 1', breed='Gir', age=5, gender='Female', health_status='Healthy')
        Cow.objects.create(name='Cow 2', breed='Gir', age=3, gender='Female', health_status='Sick')
        
        Treatment.objects.create(cow=Cow.objects.first(), disease='Disease 1', treatment_details='Details', status='Death')
        Treatment.objects.create(cow=Cow.objects.last(), disease='Disease 2', treatment_details='Details', status='Recovered')
        
        Medicine.objects.create(name='Med 1', category='Antibiotic', stock=100, unit='ml', expiry_date='2025-12-31')
        Medicine.objects.create(name='Med 2', category='Vitamin', stock=50, unit='tablet', expiry_date='2025-12-31')
        
        self.dashboard_url = reverse('doctor-dashboard')

    def test_doctor_dashboard_stats(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data['stats']
        self.assertEqual(stats['total_deaths'], 1)
        self.assertEqual(stats['total_cows'], 2)
        self.assertEqual(stats['total_medicines_stock'], 150)
