from rest_framework import viewsets, permissions
from .models import Cow
from .serializers import CowSerializer

class CowViewSet(viewsets.ModelViewSet):
    queryset = Cow.objects.all()
    serializer_class = CowSerializer
    permission_classes = [permissions.IsAuthenticated] # Keep it secure
