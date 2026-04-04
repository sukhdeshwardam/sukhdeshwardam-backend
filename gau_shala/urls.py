"""
Root URL configuration – Pure REST API, no HTML pages.
All auth endpoints are prefixed with /api/auth/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "status": "ok",
        "message": "Gau Shala API is running"
    })

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/auth/',    include('accounts.urls')),
    path('api/blog/',    include('blog.urls')),
    path('api/gallery/', include('gallery.urls')),
    path('api/cattle/',  include('cattle.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/medical/', include('medical.urls')),
    path('api/management/', include('management.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
