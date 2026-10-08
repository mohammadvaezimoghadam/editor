from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from .views import ai_playground

urlpatterns = [
    # Interactive AI test playground
    path("", ai_playground, name="ai_playground"),
    
    # Pure Django REST Framework AI endpoints for mobile & Flutter
    path("api/v1/ai/", include("wagtail_ai.api_urls")),
    
    # Static & media file handling
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *staticfiles_urlpatterns(),
]
