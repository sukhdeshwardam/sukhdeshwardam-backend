from rest_framework import viewsets, permissions
from .models import Medicine, CowFoodStock, MedicineUsage
from .serializers import MedicineSerializer, CowFoodStockSerializer, MedicineUsageSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [permissions.IsAuthenticated]

class CowFoodStockViewSet(viewsets.ModelViewSet):
    queryset = CowFoodStock.objects.all()
    serializer_class = CowFoodStockSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedicineUsageViewSet(viewsets.ModelViewSet):
    queryset = MedicineUsage.objects.all()
    serializer_class = MedicineUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
