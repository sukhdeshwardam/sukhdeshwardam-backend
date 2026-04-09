from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Medicine, CowFoodStock, MedicineUsage, MedicalStore
from .serializers import MedicineSerializer, CowFoodStockSerializer, MedicineUsageSerializer, MedicalStoreSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='pay-by-bill')
    def pay_by_bill(self, request):
        bill_number = request.data.get('bill_number')
        gst_amount_str = request.data.get('gst_amount', 0)
        
        if not bill_number:
            return Response({"error": "Bill number is required"}, status=400)
            
        try:
            gst_amount = Decimal(str(gst_amount_str))
        except (ValueError, TypeError):
            return Response({"error": "Invalid GST amount"}, status=400)
            
        medicines = self.get_queryset().filter(bill_number=bill_number)
        if not medicines.exists():
            return Response({"error": "No medicines found for this bill number"}, status=404)
            
        total_base_price = sum(med.total_price for med in medicines)
        
        if total_base_price == Decimal('0'):
            # Edge case if all medicines happen to have 0 price
            count = Decimal(str(medicines.count()))
            gst_per_item = gst_amount / count
            for med in medicines:
                current_gst = med.gst_amount or Decimal('0')
                med.gst_amount = current_gst + gst_per_item
                med.total_price += gst_per_item
                med.paid = med.total_price
                med.save()
        else:
            for med in medicines:
                proportion = med.total_price / total_base_price
                med_gst = gst_amount * proportion
                
                # Update GST and prices
                current_gst = med.gst_amount or Decimal('0')
                med.gst_amount = current_gst + med_gst
                med.total_price += med_gst
                med.paid = med.total_price
                med.save()
                
        return Response({"message": f"Successfully paid bill {bill_number} and applied GST."})

class CowFoodStockViewSet(viewsets.ModelViewSet):
    queryset = CowFoodStock.objects.all()
    serializer_class = CowFoodStockSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedicineUsageViewSet(viewsets.ModelViewSet):
    queryset = MedicineUsage.objects.all()
    serializer_class = MedicineUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedicalStoreViewSet(viewsets.ModelViewSet):
    queryset = MedicalStore.objects.all()
    serializer_class = MedicalStoreSerializer
    permission_classes = [permissions.IsAuthenticated]
