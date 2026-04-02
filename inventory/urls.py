from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, CowFoodStockViewSet, MedicineUsageViewSet, MedicalStoreViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'foods', CowFoodStockViewSet, basename='cow-food')
router.register(r'usage', MedicineUsageViewSet, basename='medicine-usage')
router.register(r'medical-stores', MedicalStoreViewSet, basename='medical-store')

urlpatterns = [
    path('', include(router.urls)),
]
