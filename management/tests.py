from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from management.models import Visitor, Visit

class VisitTests(APITestCase):
    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            email='doctor@example.com',
            password='password123',
            first_name='Doctor',
            last_name='Who',
            role=CustomUser.Role.DOCTOR
        )
        self.client.force_authenticate(user=self.doctor)
        self.visitor = Visitor.objects.create(
            name='John Doe',
            phone='1234567890',
            address='123 Main St',
            added_by=self.doctor
        )
        self.visit_url = reverse('visit-list')

    def test_create_visit(self):
        data = {
            'visitor': self.visitor.id,
            'visit_date': '2023-10-27',
            'notes': 'Regular checkup'
        }
        response = self.client.post(self.visit_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(Visit.objects.get().notes, 'Regular checkup')

    def test_create_visitor_with_empty_dob(self):
        data = {
            'name': 'Bob Burger',
            'phone': '5551234567',
            'dob': '', # Empty string which was causing 500
            'address': 'Ocean Ave'
        }
        response = self.client.post(self.visit_url.replace('visits', 'visitors'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Visitor.objects.get(phone='5551234567').dob)
