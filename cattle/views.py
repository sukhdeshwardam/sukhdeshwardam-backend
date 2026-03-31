from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cow, CowBaseStats
from .serializers import CowSerializer, CowBaseStatsSerializer

class CowViewSet(viewsets.ModelViewSet):
    queryset = Cow.objects.all()
    serializer_class = CowSerializer
    permission_classes = [permissions.IsAuthenticated] # Keep it secure

class CowBaseStatsViewSet(viewsets.ModelViewSet):
    queryset = CowBaseStats.objects.all()
    serializer_class = CowBaseStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        stat = CowBaseStats.load()
        serializer = self.get_serializer(stat)
        return Response(serializer.data)
