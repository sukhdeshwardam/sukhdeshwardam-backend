from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TreatmentViewSet, SymptomViewSet, DiseaseViewSet

router = DefaultRouter()
router.register(r'treatment', TreatmentViewSet, basename='treatment')
router.register(r'symptoms', SymptomViewSet)
router.register(r'diseases', DiseaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
