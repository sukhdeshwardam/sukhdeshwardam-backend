from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisitorViewSet, DonorViewSet, DonationViewSet, VisitViewSet, SendCampaignView
router = DefaultRouter()
router.register(r'visitors', VisitorViewSet)
router.register(r'donors', DonorViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'visits', VisitViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-campaign/', SendCampaignView.as_view(), name='send-campaign'),
]
