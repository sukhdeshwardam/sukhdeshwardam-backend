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
        
        # Always create a new visitor record (no merging)
        visitor = Visitor.objects.create(phone=phone, added_by=self.request.user, **visitor_data)
            
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
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

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
        
        # Always create a new donor record (no merging)
        donor = Donor.objects.create(**donor_data)

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
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
import requests
import json
import re
import os
import cloudinary.uploader

class SendCampaignView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        data = request.data
        target = data.get('target')  # 'donors', 'visitors', 'both', 'specific'
        message_text = data.get('message', '')
        api_key = data.get('api_key') or os.environ.get('fast2sms_api_key')
        specific_ids = data.get('specific_ids', [])
        
        if isinstance(specific_ids, str):
            try:
                specific_ids = json.loads(specific_ids)
            except:
                specific_ids = []

        if not api_key:
            return response.Response({'error': 'Fast2SMS API Key is required.'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get('image')
        # Also allow passing a pre-hosted image URL directly (e.g. for birthday wishes)
        image_url_direct = data.get('image_url', '').strip()
        image_url = None

        if image_file:
            try:
                upload_data = cloudinary.uploader.upload(image_file)
                image_url = upload_data.get('secure_url')
            except Exception as e:
                return response.Response({'error': f'Failed to upload image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        elif image_url_direct:
            # Use the pre-hosted URL directly (no upload needed)
            image_url = image_url_direct
        else:
            # Header image is REQUIRED by the approved gau_dham template
            return response.Response({'error': 'A header image is required by the approved WhatsApp template.'}, status=status.HTTP_400_BAD_REQUEST)

        if not message_text.strip():
            return response.Response({'error': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        phones = set()

        if target in ['donors', 'both']:
            donors = Donor.objects.exclude(phone__isnull=True).exclude(phone__exact='')
            for d in donors:
                phones.add(d.phone)
        
        if target in ['visitors', 'both']:
            visitors = Visitor.objects.exclude(phone__isnull=True).exclude(phone__exact='')
            for v in visitors:
                phones.add(v.phone)
        
        if target == 'specific' and specific_ids:
            for item_id in specific_ids:
                if str(item_id).startswith('donor_'):
                    d_id = item_id.split('_')[1]
                    try:
                        d = Donor.objects.get(id=d_id)
                        if d.phone:
                            phones.add(d.phone)
                    except Donor.DoesNotExist:
                        pass
                elif str(item_id).startswith('visitor_'):
                    v_id = item_id.split('_')[1]
                    try:
                        v = Visitor.objects.get(id=v_id)
                        if v.phone:
                            phones.add(v.phone)
                    except Visitor.DoesNotExist:
                        pass
        
        clean_phones = set()
        for p in phones:
            cleaned = re.sub(r'\D', '', p)
            if len(cleaned) > 10 and cleaned.endswith(cleaned[-10:]):
                cleaned = cleaned[-10:]
            if len(cleaned) == 10:
                clean_phones.add(cleaned)
        
        clean_phones = list(clean_phones)
        
        if not clean_phones:
            return response.Response({'error': 'No valid 10-digit phone numbers found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Note: clean_phones is already a set() so duplicate numbers selected in
        # the same request are automatically deduplicated — one charge per unique number.

        # The correct Fast2SMS WhatsApp endpoint
        url = "https://www.fast2sms.com/dev/whatsapp"
        
        # Fast2SMS requires phone_number_id for WhatsApp
        phone_number_id = os.environ.get('FAST2SMS_PHONE_ID', '') 

        if not phone_number_id:
            return response.Response({'error': 'Fast2SMS Phone Number ID (.env FAST2SMS_PHONE_ID) is required for WhatsApp route.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build payload based on Fast2SMS WhatsApp Simple API
        # gau_dham template has ONE variable: {{1}} = message body
        # Header image is sent via media_url
        payload = {
            "message_id": "17526",  # Message ID from Fast2SMS dashboard
            "phone_number_id": phone_number_id,
            "variables_values": message_text,   # {{1}} only
            "numbers": ",".join(clean_phones),
            "media_url": image_url,  # header image (required)
        }
        
        headers = {
            'authorization': api_key,  # API key must be in header
            'Content-Type': "application/json",
            'Accept': "application/json"
        }
        
        try:
            r = requests.post(url, json=payload, headers=headers)
            r_data = r.json()
            if r_data.get('return'):
                return response.Response({'success': True, 'message': f'Message queued for {len(clean_phones)} numbers.', 'fast2sms_response': r_data}, status=status.HTTP_200_OK)
            else:
                return response.Response({'error': 'Fast2SMS Error', 'details': r_data}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BirthdayListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import date
        import re
        today = date.today()
        
        # Donors with birthday today
        donors = Donor.objects.filter(dob__month=today.month, dob__day=today.day)
        donor_data = [
            {'id': f'donor_{d.id}', 'name': d.name, 'phone': d.phone, 'type': 'Donor'}
            for d in donors
        ]
        
        # Visitors with birthday today
        visitors = Visitor.objects.filter(dob__month=today.month, dob__day=today.day)
        visitor_data = [
            {'id': f'visitor_{v.id}', 'name': v.name, 'phone': v.phone, 'type': 'Visitor'}
            for v in visitors
        ]
        
        # Deduplicate combined list by phone number
        combined = donor_data + visitor_data
        deduplicated = {}
        for item in combined:
            phone = item.get('phone')
            if not phone: continue
            
            cleaned_phone = re.sub(r'\D', '', phone)
            if len(cleaned_phone) > 10 and cleaned_phone.endswith(cleaned_phone[-10:]):
                cleaned_phone = cleaned_phone[-10:]
                
            if len(cleaned_phone) != 10:
                cleaned_phone = phone # fallback if it's completely weird

            # If phone exists, prioritize Donor
            if cleaned_phone not in deduplicated or item['type'] == 'Donor':
                deduplicated[cleaned_phone] = item
                
        return response.Response(list(deduplicated.values()), status=status.HTTP_200_OK)
