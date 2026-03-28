from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CowViewSet

router = DefaultRouter()
router.register(r'', CowViewSet, basename='cow')

urlpatterns = [
    path('', include(router.urls)),
]
