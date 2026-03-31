from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CowViewSet, CowBaseStatsViewSet

router = DefaultRouter()
router.register(r'base-stats', CowBaseStatsViewSet, basename='cow-base-stats')
router.register(r'', CowViewSet, basename='cow')

urlpatterns = [
    path('', include(router.urls)),
]
