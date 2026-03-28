from rest_framework import viewsets, permissions
from .models import Visitor, Donor, Donation, Visit
from .serializers import VisitorSerializer, DonorSerializer, DonationSerializer, VisitSerializer

class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all().order_by('-created_at')
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return response.Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        dob = request.data.get('dob')
        visitor_data = {
            'name': request.data.get('name'),
            'email': request.data.get('email', ''),
            'dob': dob if dob else None,
            'address': request.data.get('address', ''),
        }
        
        # Get or create visitor by phone
        visitor, created = Visitor.objects.get_or_create(phone=phone, defaults=visitor_data)
        
        # Update info if already exists but new info provided
        if not created:
            for key, value in visitor_data.items():
                if value:
                    setattr(visitor, key, value)
            visitor.save()

        # If it was created, we also need to set added_by which wasn't in defaults or defaults might not handle it well with ForeignKey
        if created:
            visitor.added_by = self.request.user
            visitor.save()
            
        # Log an initial visit if visit_date is provided
        visit_date = request.data.get('visit_date')
        if visit_date:
            visit_time = request.data.get('visit_time')
            notes = request.data.get('notes', 'Initial registration visit')
            Visit.objects.create(
                visitor=visitor,
                visit_date=visit_date,
                visit_time=visit_time if visit_time else None,
                notes=notes
            )
            
        serializer = self.get_serializer(visitor)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def perform_create(self, serializer):
        # This is now handled by our custom create method
        pass

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all().order_by('-created_at')
    serializer_class = DonorSerializer
    permission_classes = [permissions.IsAuthenticated]

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Extract donor profile info from request
        dob = request.data.get('dob')
        donor_data = {
            'name': request.data.get('name'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'dob': dob if dob else None,
            'address': request.data.get('address'),
        }
        
        # Find or create donor by phone
        phone = donor_data.get('phone')
        donor, created = Donor.objects.get_or_create(phone=phone, defaults=donor_data)
        
        # If donor existed, update their profile just in case info changed
        if not created:
            for key, value in donor_data.items():
                if value:
                    setattr(donor, key, value)
            donor.save()
            
        # Log the donation
        donation_data = request.data.copy()
        donation_data['donor'] = donor.id
        
        serializer = self.get_serializer(data=donation_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(added_by=self.request.user)
        
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all().order_by('-visit_date')
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework import response, status
